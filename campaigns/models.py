from django.conf import settings
from django.db import models


class EmailAccount(models.Model):
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('custom', 'Custom SMTP'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_accounts')
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default='gmail')
    email_address = models.EmailField()
    smtp_host = models.CharField(max_length=255, default='smtp.gmail.com')
    smtp_port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    imap_host = models.CharField(max_length=255, default='imap.gmail.com')
    encrypted_password = models.TextField(help_text='Encrypted SMTP/app password')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'email_address')
        ordering = ['-created_at']

    def __str__(self):
        return self.email_address


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Queued', 'Queued'),
        ('Sending', 'Sending'),
        ('Completed', 'Completed'),
        ('Paused', 'Paused'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    email_account = models.ForeignKey(EmailAccount, on_delete=models.PROTECT, related_name='campaigns')
    name = models.CharField(max_length=255, help_text='Internal campaign name')
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text='Use {name}, or start with "Hi," and the system will add the name.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Recipient(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Queued', 'Queued'),
        ('Sending', 'Sending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
        ('Replied', 'Replied'),
        ('Bounced', 'Bounced'),
        ('Unsubscribed', 'Unsubscribed'),
        ('Skipped', 'Skipped'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    name = models.CharField(max_length=255, blank=True, default='Valued Client')
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    last_sent = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    reply_text = models.TextField(blank=True, null=True)
    sent_message_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campaign', 'email')
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.email})'


class SuppressionList(models.Model):
    REASON_CHOICES = [
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('manual', 'Manual block'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suppression_items')
    email = models.EmailField()
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='unsubscribed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'email')

    def __str__(self):
        return f'{self.email} - {self.reason}'
