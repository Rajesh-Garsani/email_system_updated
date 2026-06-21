from django.core.management.base import BaseCommand
from django.conf import settings
from campaigns.services import send_queued_emails


class Command(BaseCommand):
    help = 'Send queued campaign emails safely in small batches.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=settings.DEFAULT_SEND_BATCH_LIMIT)
        parser.add_argument('--delay', type=int, default=settings.DEFAULT_SEND_DELAY_SECONDS)

    def handle(self, *args, **options):
        result = send_queued_emails(limit=options['limit'], delay_seconds=options['delay'])
        self.stdout.write(self.style.SUCCESS(f"Sent: {result['sent']}, Failed: {result['failed']}"))
