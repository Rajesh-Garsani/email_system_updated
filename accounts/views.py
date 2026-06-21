import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import get_connection, EmailMessage
from django.db import transaction

from .forms import RegisterForm
from campaigns.models import EmailAccount
from campaigns.security import encrypt_password


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            app_password = form.cleaned_data["email_app_password"]

            # 1. Generate a secure 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # 2. Test the user's App Password by sending the OTP to themselves
            try:
                connection = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host='smtp.gmail.com',
                    port=587,
                    username=email,
                    password=app_password,
                    use_tls=True,
                    timeout=15,  # Wait max 15 seconds to check
                )

                message = EmailMessage(
                    subject="Your CampaignManager Security Code",
                    body=f"Hello {username},\n\nYour security verification code is: {otp}\n\nUse this code to complete your registration. If you did not request this, please ignore this email.\n\n- CampaignManager Security",
                    from_email=email,
                    to=[email],
                    connection=connection,
                )
                message.send(fail_silently=False)

                # 3. If successful, store data in session and redirect
                request.session['registration_data'] = {
                    'email': email,
                    'username': username,
                    'password': password,
                    'app_password': app_password,
                    'otp': otp
                }

                messages.info(request, "We sent a security code to your email. Please enter it below.")
                return redirect('verify_otp')

            except Exception as e:
                # If the app password is wrong, tell them instantly!
                messages.error(request,
                               "Failed to connect to Gmail. Are you sure you used an App Password (not your normal password) and typed it correctly?")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def verify_otp_view(request):
    # Check if session data exists
    reg_data = request.session.get('registration_data')
    if not reg_data:
        messages.error(request, "Session expired or invalid. Please start registration again.")
        return redirect('register')

    if request.method == "POST":
        entered_otp = request.POST.get('otp', '').strip()

        if entered_otp == reg_data['otp']:
            # Success! Create the user securely in an atomic transaction
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        email=reg_data['email'],
                        password=reg_data['password']
                    )

                    EmailAccount.objects.create(
                        user=user,
                        provider="gmail",
                        email_address=reg_data['email'],
                        smtp_host="smtp.gmail.com",
                        smtp_port=587,
                        use_tls=True,
                        imap_host="imap.gmail.com",
                        encrypted_password=encrypt_password(reg_data['app_password']),
                        is_active=True,
                    )

                # Clear session so OTP can't be reused
                del request.session['registration_data']

                # Log them in and send to dashboard
                login(request, user)
                messages.success(request, "Account verified and created successfully! Your sending account is ready.")
                return redirect("dashboard")

            except Exception as e:
                messages.error(request, f"Database error during registration: {e}")
        else:
            messages.error(request, "Invalid security code. Please try again.")

    return render(request, "accounts/verify_otp.html", {'email': reg_data['email']})