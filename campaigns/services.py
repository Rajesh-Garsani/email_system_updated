import re
import time
import email as email_parser
from typing import Dict

import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, get_connection
from django.core.validators import validate_email
from django.db.models import Count
from django.utils import timezone
from imapclient import IMAPClient

from .models import Recipient, Campaign, SuppressionList, EmailAccount
from .security import decrypt_value


ALLOWED_EXTENSIONS = ('.csv', '.xlsx')


def personalize_body(body: str, recipient: Recipient) -> str:
    """Supports both 'Hi {name},' and automatic conversion of first-line 'Hi,' to 'Hi John,'."""
    name = (recipient.name or '').strip() or 'there'

    if '{name}' in body:
        return body.replace('{name}', name)

    greeting_patterns = [
        (r'^Hi,\s*', f'Hi {name},\n\n'),
        (r'^Hello,\s*', f'Hello {name},\n\n'),
        (r'^Dear,\s*', f'Dear {name},\n\n'),
    ]

    for pattern, replacement in greeting_patterns:
        if re.match(pattern, body, flags=re.IGNORECASE):
            return re.sub(pattern, replacement, body, count=1, flags=re.IGNORECASE)

    return body


def process_uploaded_file(file, campaign: Campaign) -> Dict[str, int]:
    """Validate CSV/XLSX file and import recipients safely."""
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(f'File is too large. Maximum allowed size is {settings.MAX_UPLOAD_MB} MB.')

    filename = file.name.lower()
    if not filename.endswith(ALLOWED_EXTENSIONS):
        raise ValidationError('Only .csv and .xlsx files are allowed.')

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as exc:
        raise ValidationError(f'Could not read uploaded file: {exc}')

    df.columns = [str(col).strip() for col in df.columns]
    required = {'Name', 'Email'}
    missing = required - set(df.columns)
    if missing:
        raise ValidationError(f'Missing required columns: {", ".join(sorted(missing))}')

    if len(df) > settings.MAX_RECIPIENTS_PER_CAMPAIGN:
        raise ValidationError(
            f'Too many rows. Maximum allowed recipients per campaign is '
            f'{settings.MAX_RECIPIENTS_PER_CAMPAIGN}.'
        )

    created = 0
    skipped = 0

    for _, row in df.iterrows():
        raw_email = str(row.get('Email', '')).strip().lower()
        raw_name = str(row.get('Name', '')).strip()

        if not raw_email or raw_email == 'nan':
            skipped += 1
            continue

        try:
            validate_email(raw_email)
        except ValidationError:
            skipped += 1
            continue

        if SuppressionList.objects.filter(user=campaign.user, email=raw_email).exists():
            skipped += 1
            continue

        name = raw_name if raw_name and raw_name.lower() != 'nan' else 'Valued Client'
        _, was_created = Recipient.objects.get_or_create(
            campaign=campaign,
            email=raw_email,
            defaults={'name': name},
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return {'created': created, 'skipped': skipped}


def queue_campaign(campaign: Campaign) -> int:
    """Queue all pending/failed recipients. Actual sending should be handled by management command."""
    recipients = campaign.recipients.filter(status__in=['Pending', 'Failed'])
    queued = 0
    for recipient in recipients:
        if SuppressionList.objects.filter(user=campaign.user, email=recipient.email).exists():
            recipient.status = 'Skipped'
            recipient.error_message = 'Email is in suppression list.'
            recipient.save(update_fields=['status', 'error_message'])
            continue
        recipient.status = 'Queued'
        recipient.error_message = ''
        recipient.save(update_fields=['status', 'error_message'])
        queued += 1

    campaign.status = 'Queued' if queued else campaign.status
    campaign.save(update_fields=['status', 'updated_at'])
    return queued



def send_campaign_now(campaign: Campaign, limit: int = None, delay_seconds: int = 0) -> Dict[str, int]:
    """
    Simple user-friendly sending: user clicks Send Emails and this sends a small batch immediately.
    It keeps safety limits, daily limits, validation, and personalization, but hides the manual queue command.
    """
    limit = limit or settings.DEFAULT_SEND_BATCH_LIMIT

    # Convert pending/failed recipients into queued state first.
    queue_campaign(campaign)

    recipients = Recipient.objects.select_related('campaign', 'campaign__email_account').filter(
        campaign=campaign,
        status='Queued',
        campaign__email_account__is_active=True,
    ).order_by('id')[:limit]

    sent = 0
    failed = 0

    for recipient in recipients:
        success = send_one_recipient(recipient)
        if success:
            sent += 1
        else:
            failed += 1

        if delay_seconds and delay_seconds > 0:
            time.sleep(delay_seconds)

    # Refresh only this campaign's visible status.
    remaining = campaign.recipients.filter(status__in=['Pending', 'Failed', 'Queued', 'Sending']).exists()
    if remaining:
        campaign.status = 'Sending'
    elif campaign.recipients.filter(status='Sent').exists() or campaign.recipients.filter(status='Replied').exists():
        campaign.status = 'Completed'
    else:
        campaign.status = 'Draft'
    campaign.save(update_fields=['status', 'updated_at'])

    return {'sent': sent, 'failed': failed, 'remaining': campaign.recipients.filter(status__in=['Pending', 'Failed', 'Queued']).count()}

def _email_connection(account: EmailAccount):
    password = decrypt_value(account.encrypted_password)
    return get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host=account.smtp_host,
        port=account.smtp_port,
        username=account.email_address,
        password=password,
        use_tls=account.use_tls,
        timeout=30,
    )


def daily_sent_count(account: EmailAccount) -> int:
    today = timezone.localdate()
    return Recipient.objects.filter(
        campaign__email_account=account,
        status__in=['Sent', 'Replied'],
        last_sent__date=today,
    ).count()


def send_one_recipient(recipient: Recipient) -> bool:
    """Send one queued email and update recipient status."""
    campaign = recipient.campaign
    account = campaign.email_account

    if daily_sent_count(account) >= settings.MAX_EMAILS_PER_ACCOUNT_PER_DAY:
        recipient.status = 'Failed'
        recipient.error_message = 'Daily sending limit reached for this email account.'
        recipient.save(update_fields=['status', 'error_message'])
        return False

    recipient.status = 'Sending'
    recipient.save(update_fields=['status'])

    try:
        body = personalize_body(campaign.body, recipient)
        connection = _email_connection(account)
        message = EmailMessage(
            subject=campaign.subject,
            body=body,
            from_email=account.email_address,
            to=[recipient.email],
            connection=connection,
            headers={'Reply-To': account.email_address},
        )
        message.send(fail_silently=False)
        recipient.status = 'Sent'
        recipient.error_message = ''
        recipient.last_sent = timezone.now()
        recipient.save(update_fields=['status', 'error_message', 'last_sent'])
        return True
    except Exception as exc:
        recipient.status = 'Failed'
        recipient.error_message = str(exc)[:2000]
        recipient.last_sent = timezone.now()
        recipient.save(update_fields=['status', 'error_message', 'last_sent'])
        return False


def send_queued_emails(limit: int = None, delay_seconds: int = None) -> Dict[str, int]:
    """Send a small batch of queued emails. Run using management command or scheduler."""
    limit = limit or settings.DEFAULT_SEND_BATCH_LIMIT
    delay_seconds = settings.DEFAULT_SEND_DELAY_SECONDS if delay_seconds is None else delay_seconds

    recipients = Recipient.objects.select_related('campaign', 'campaign__email_account').filter(
        status='Queued',
        campaign__email_account__is_active=True,
    ).order_by('id')[:limit]

    sent = 0
    failed = 0

    for recipient in recipients:
        success = send_one_recipient(recipient)
        if success:
            sent += 1
        else:
            failed += 1

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    _refresh_campaign_statuses()
    return {'sent': sent, 'failed': failed}


def _refresh_campaign_statuses():
    campaigns = Campaign.objects.filter(status__in=['Queued', 'Sending'])
    for campaign in campaigns:
        counts = campaign.recipients.values('status').annotate(total=Count('id'))
        status_counts = {item['status']: item['total'] for item in counts}
        if status_counts.get('Queued') or status_counts.get('Sending'):
            campaign.status = 'Sending'
        elif status_counts.get('Failed'):
            campaign.status = 'Failed'
        else:
            campaign.status = 'Completed'
        campaign.save(update_fields=['status', 'updated_at'])


def check_campaign_replies(campaign: Campaign) -> int:
    """Check unread replies for the campaign's own email account."""
    sent_recipients = campaign.recipients.filter(status='Sent')
    email_list = set(sent_recipients.values_list('email', flat=True))
    if not email_list:
        return 0

    account = campaign.email_account
    password = decrypt_value(account.encrypted_password)
    updated = 0

    with IMAPClient(account.imap_host) as server:
        server.login(account.email_address, password)
        server.select_folder('INBOX')
        messages = server.search(['UNSEEN'])

        for msg_id in messages:
            raw_message = server.fetch(msg_id, ['ENVELOPE', 'RFC822'])
            envelope = raw_message[msg_id][b'ENVELOPE']
            sender_obj = envelope.from_[0]
            sender = f'{sender_obj.mailbox.decode()}@{sender_obj.host.decode()}'.lower()

            if sender not in email_list:
                continue

            msg = email_parser.message_from_bytes(raw_message[msg_id][b'RFC822'])
            reply_body = ''

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition'))
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            reply_body = payload.decode(errors='ignore')
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    reply_body = payload.decode(errors='ignore')

            recipient = sent_recipients.filter(email=sender).first()
            if recipient:
                recipient.status = 'Replied'
                recipient.reply_text = reply_body.strip()
                recipient.save(update_fields=['status', 'reply_text'])
                updated += 1

    return updated


def send_individual_reply(recipient: Recipient, message_body: str) -> None:
    campaign = recipient.campaign
    account = campaign.email_account
    connection = _email_connection(account)
    message = EmailMessage(
        subject=f'Re: {campaign.subject}',
        body=message_body,
        from_email=account.email_address,
        to=[recipient.email],
        connection=connection,
    )
    message.send(fail_silently=False)
