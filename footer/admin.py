from django.contrib import admin
from .models import FooterSettings, FooterColumn, FooterItem, LegalPage, ResourcePage

@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()

class FooterItemInline(admin.TabularInline):
    model = FooterItem
    extra = 1

@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    inlines = [FooterItemInline]

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'last_updated')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ResourcePage)
class ResourcePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'last_updated')
    prepopulated_fields = {'slug': ('title',)}