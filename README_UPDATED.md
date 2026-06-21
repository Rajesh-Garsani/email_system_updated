# Updated Email Automation System

## Main upgrades
- Secure registration and login
- Campaign ownership per user
- Multiple users can add and use their own email accounts
- SMTP/app passwords are encrypted with Fernet
- CSV/XLSX validation with file size and recipient count limits
- Automatic greeting personalization: `Hi,` becomes `Hi John,`
- Safe queue-based sending instead of blocking browser requests
- Batch sending command with delay to reduce provider blocking/spam risk

## Generate encryption key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste it into `.env` as `FIELD_ENCRYPTION_KEY`.

## Recommended safe limits for your current architecture
For SQLite/shared hosting/PythonAnywhere-style deployment:
- Upload size: 2 MB
- Recipients per campaign: 500 to 1000
- Per account daily emails: 50 to 100 for Gmail
- Batch size: 10 to 20 emails
- Delay: 30 to 60 seconds between emails

For better production architecture:
- Use PostgreSQL
- Use Redis + Celery
- Use SPF, DKIM, DMARC
- Use verified business domains
- Add unsubscribe links and suppression list enforcement

## Run sending command
```bash
python manage.py send_queued_emails --limit 20 --delay 30
```

On PythonAnywhere, add this as a scheduled task.
