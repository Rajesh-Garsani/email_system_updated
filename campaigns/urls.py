from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('email-accounts/', views.email_accounts, name='email_accounts'),
    path('campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaign/<int:pk>/send/', views.trigger_send, name='trigger_send'),
    path('campaign/<int:pk>/check-replies/', views.trigger_check_replies, name='trigger_check_replies'),
    path('recipient/<int:recipient_id>/reply/', views.send_reply_view, name='send_reply'),
]
