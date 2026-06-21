from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Campaign, EmailAccount
from .security import encrypt_password


class CampaignForm(forms.ModelForm):
    contact_file = forms.FileField(
        required=True,
        help_text="Upload CSV or Excel file with Name and Email columns.",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": ".csv,.xlsx"
        })
    )

    class Meta:
        model = Campaign
        fields = ["name", "subject", "body"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Web Design Outreach"
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Quick question about your business"
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 7,
                "placeholder": "Hi,\n\nI hope you are doing well..."
            }),
        }

    def clean_contact_file(self):
        file = self.cleaned_data.get("contact_file")

        if not file:
            raise ValidationError("Please upload a CSV or Excel file.")

        filename = file.name.lower()

        if not (filename.endswith(".csv") or filename.endswith(".xlsx")):
            raise ValidationError("Only CSV and XLSX files are allowed.")

        max_size = settings.MAX_UPLOAD_MB * 1024 * 1024

        if file.size > max_size:
            raise ValidationError(
                f"File size must be less than {settings.MAX_UPLOAD_MB} MB."
            )

        return file


class EmailAccountForm(forms.ModelForm):
    app_password = forms.CharField(
        required=True,
        label="Gmail App Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Gmail App Password"
        }),
        help_text="Use Gmail App Password, not your normal Gmail password."
    )

    class Meta:
        model = EmailAccount
        fields = ["email_address", "app_password"]
        widgets = {
            "email_address": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Gmail address"
            }),
        }

    def save(self, commit=True):
        email_account = super().save(commit=False)

        app_password = self.cleaned_data["app_password"]

        email_account.provider = "gmail"
        email_account.smtp_host = "smtp.gmail.com"
        email_account.smtp_port = 587
        email_account.use_tls = True
        email_account.imap_host = "imap.gmail.com"
        email_account.encrypted_password = encrypt_password(app_password)
        email_account.is_active = True

        if commit:
            email_account.save()

        return email_account