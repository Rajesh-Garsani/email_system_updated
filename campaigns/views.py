from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
import threading
from .forms import CampaignForm, EmailAccountForm
from .models import Campaign, EmailAccount, Recipient
from .services import (
    process_uploaded_file,
    check_campaign_replies,
    send_individual_reply,
    send_campaign_background, queue_campaign,
)


@login_required
def dashboard(request):
    campaigns = Campaign.objects.filter(user=request.user).select_related('email_account')
    default_account = EmailAccount.objects.filter(user=request.user, is_active=True).first()

    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            if not default_account:
                messages.error(request, 'No sending email found. Please register again or add Gmail App Password in Advanced Email Settings.')
                return redirect('dashboard')

            campaign = None
            try:
                campaign = form.save(commit=False)
                campaign.user = request.user
                campaign.email_account = default_account
                campaign.status = 'Draft'
                campaign.save()

                result = process_uploaded_file(request.FILES['contact_file'], campaign)
                messages.success(
                    request,
                    f"Campaign created successfully. Imported {result['created']} recipients; skipped {result['skipped']} invalid/duplicate rows."
                )
                return redirect('campaign_detail', pk=campaign.pk)
            except ValidationError as exc:
                if campaign and campaign.pk:
                    campaign.delete()
                message = exc.message if hasattr(exc, 'message') else exc.messages[0]
                messages.error(request, message)
    else:
        form = CampaignForm()

    return render(request, 'campaigns/dashboard.html', {
        'campaigns': campaigns,
        'form': form,
        'default_account': default_account,
    })


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(
        Campaign.objects.select_related('email_account'),
        pk=pk,
        user=request.user,
    )
    return render(request, 'campaigns/detail.html', {'campaign': campaign})


@login_required
@require_POST
def trigger_send(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)

    try:
        # 1. Immediately mark the campaign as queued so the UI updates
        queue_campaign(campaign)

        # 2. Start the background thread
        # We pass the campaign.id instead of the object to prevent memory issues between threads
        thread = threading.Thread(
            target=send_campaign_background,
            args=(campaign.id, None, 2)
            # Adding a 2-second delay between emails prevents Gmail from blocking the account
        )
        thread.daemon = True  # This ensures the thread dies if the main web server restarts
        thread.start()

        messages.success(request,
                         "🚀 Campaign started! Emails are sending securely in the background. Refresh the page to see live updates.")

    except Exception as exc:
        messages.error(request, f'Could not start campaign: {exc}')

    return redirect('campaign_detail', pk=pk)


@login_required
@require_POST
def trigger_check_replies(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, user=request.user)
    try:
        updated = check_campaign_replies(campaign)
        messages.success(request, f'Inbox checked. {updated} replies found.')
    except Exception as exc:
        messages.error(request, f'Could not check replies: {exc}')
    return redirect('campaign_detail', pk=pk)


@login_required
@require_POST
def send_reply_view(request, recipient_id):
    recipient = get_object_or_404(
        Recipient.objects.select_related('campaign', 'campaign__email_account'),
        pk=recipient_id,
        campaign__user=request.user,
    )
    reply_message = request.POST.get('reply_message', '').strip()

    if not reply_message:
        messages.error(request, 'Message cannot be empty.')
        return redirect('campaign_detail', pk=recipient.campaign.pk)

    try:
        send_individual_reply(recipient, reply_message)
        messages.success(request, f'Reply sent to {recipient.name}.')
    except Exception as exc:
        messages.error(request, f'Failed to send reply: {exc}')

    return redirect('campaign_detail', pk=recipient.campaign.pk)


@login_required
def email_accounts(request):
    """Advanced page. Normal users do not need this because registration auto-configures Gmail."""
    accounts = EmailAccount.objects.filter(user=request.user)

    if request.method == 'POST':
        form = EmailAccountForm(request.POST)
        if form.is_valid():
            try:
                form.save(user=request.user)
                messages.success(request, 'Email account added successfully.')
                return redirect('email_accounts')
            except Exception as exc:
                messages.error(request, f'Could not save email account: {exc}')
    else:
        form = EmailAccountForm()

    return render(request, 'campaigns/email_accounts.html', {'accounts': accounts, 'form': form})
