from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Gmail Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your Gmail address",
        })
    )

    email_app_password = forms.CharField(
        required=True,
        label="Gmail App Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Gmail App Password",
        }),
        help_text="Use Gmail App Password, not your normal Gmail password."
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "email_app_password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter username",
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email:
            email = email.lower().strip()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")

        return email