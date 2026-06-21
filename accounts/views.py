from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegisterForm
from campaigns.models import EmailAccount
from campaigns.security import encrypt_password


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            app_password = form.cleaned_data["email_app_password"]

            EmailAccount.objects.create(
                user=user,
                provider="gmail",
                email_address=user.email,
                smtp_host="smtp.gmail.com",
                smtp_port=587,
                use_tls=True,
                imap_host="imap.gmail.com",
                encrypted_password=encrypt_password(app_password),
                is_active=True,
            )

            login(request, user)

            messages.success(
                request,
                "Account created successfully. Your Gmail sending account is ready."
            )

            return redirect("dashboard")



    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})