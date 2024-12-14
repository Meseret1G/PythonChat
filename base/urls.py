from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('<str:username>/',views.chatPage,name='chat')
    # path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    # path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    # path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    # path('send-message/', views.send_message, name='send_message'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
