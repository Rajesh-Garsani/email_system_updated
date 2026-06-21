from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_fernet():
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "")

    if not key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY is missing. Add it to your .env file."
        )

    try:
        return Fernet(key.encode())
    except Exception:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY is invalid. Generate a valid key using: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )


def encrypt_password(raw_password):
    if not raw_password:
        return ""

    fernet = get_fernet()
    return fernet.encrypt(raw_password.encode()).decode()


def decrypt_password(encrypted_password):
    if not encrypted_password:
        return ""

    try:
        fernet = get_fernet()
        return fernet.decrypt(encrypted_password.encode()).decode()
    except InvalidToken:
        raise ImproperlyConfigured(
            "Cannot decrypt email password. FIELD_ENCRYPTION_KEY may have changed."
        )


# Backward-compatible aliases for old project files
def encrypt_value(raw_value):
    return encrypt_password(raw_value)


def decrypt_value(encrypted_value):
    return decrypt_password(encrypted_value)