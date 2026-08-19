"""URL patterns for accounts app."""
from django.urls import path

from .views import SignupView, login_view, logout_view

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
