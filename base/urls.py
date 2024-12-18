from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.index, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_username'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('edit/', views.edit_user_info, name='edit_user_info'),  
    path('chat/<str:username>/', views.chatPage, name='chat'),
    path('get-user-info/<str:username>/', views.get_user_info, name='get_user_info'),
    path('search-users/', views.search_users, name='search_users'),

    path('send-friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('are-friends/<str:username>/', views.are_friends, name='are_friends'),
    path('remove_friend/<str:username>/', views.remove_friend, name='remove_friend'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
