from django.urls import path
from . import  views


#URL patterns for the homepage, userprofile, help documentation,email, repo dashboard, code quality, and url deletion pages.
urlpatterns = [
    path('', views.home, name='wdg-home'),
    path('profile/', views.profile, name='wdg-profile'),
    path('help/', views.help, name='wdg-help'),
    path('dashboard/<int:url_id>/email', views.send_email_view, name='wdg-email'),
    path('dashboard/<int:url_id>/', views.dashboard, name='wdg-dashboard'),
    path('dashboard/<int:url_id>/codequality', views.codequality, name='wdg-codequality'),
    path('delete/<int:url_id>/', views.delete_url, name='wdg-deleteurl'),
]