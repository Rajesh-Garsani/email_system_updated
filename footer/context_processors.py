from .models import FooterSettings, FooterColumn

def footer_data(request):
    settings = FooterSettings.objects.first()
    columns = FooterColumn.objects.prefetch_related('items').all()

    return {
        'footer_settings': settings,
        'footer_columns': columns,
    }