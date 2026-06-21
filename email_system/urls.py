from django.contrib import admin
from django.urls import path, include
from footer import views as footer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('campaigns.urls')),

    path('privacy/', footer_views.legal_page_view, {'slug': 'privacy'}, name='privacy'),
    path('terms/', footer_views.legal_page_view, {'slug': 'terms'}, name='terms'),
    path('resources/<slug:slug>/', footer_views.resource_page_view, name='resource_page'),
]
