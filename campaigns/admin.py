from django.contrib import admin
from .models import EmailAccount, Campaign, Recipient, SuppressionList


@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'user', 'provider', 'is_active', 'created_at')
    search_fields = ('email_address', 'user__username')


class RecipientInline(admin.TabularInline):
    model = Recipient
    extra = 0
    readonly_fields = ('last_sent', 'error_message', 'reply_text')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'email_account', 'status', 'created_at')
    search_fields = ('name', 'subject', 'user__username')
    inlines = [RecipientInline]


@admin.register(SuppressionList)
class SuppressionListAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'reason', 'created_at')
    search_fields = ('email', 'user__username')
