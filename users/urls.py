from django.urls import path
from django.contrib.auth import views as auth_views
from . import  views

#Url patterns for login, register, password reset and logout pages.
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='wdg-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='wdg-logout'),
    path('passwordreset/', auth_views.PasswordResetView.as_view(template_name='registration/passwordreset.html'), name='wdg-passwordreset'),
    path('signup/', views.signup, name='wdg-signup'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]