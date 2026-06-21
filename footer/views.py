from django.shortcuts import render, get_object_or_404
from .models import LegalPage, ResourcePage

def legal_page_view(request, slug):
    page = get_object_or_404(LegalPage, slug=slug)
    return render(request, 'footer/legal_page.html', {'page': page})

def resource_page_view(request, slug):
    page = get_object_or_404(ResourcePage, slug=slug)
    return render(request, 'footer/resource_page.html', {'page': page})