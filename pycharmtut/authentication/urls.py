from django.urls import path
from .views import LoginView, RegisterUsersView, ApiListUsers, ApiDeleteUser, ForgotEmailView, ProfileView,\
    ProfilePasswordChangeView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/password/', ForgotEmailView.as_view(), name="auth-pass"),
    path('auth/register/', RegisterUsersView.as_view(), name="auth-register"),
    path('auth/users/<str:id>', ApiListUsers.as_view(), name="auth-list"),
    path('auth/delete/<str:id>', ApiDeleteUser.as_view(), name='user-delete'),
    path('auth/profile/', ProfileView.as_view(), name='user-update'),
    path('auth/profile-pass/', ProfilePasswordChangeView.as_view(), name='user-update-pass'),
]
