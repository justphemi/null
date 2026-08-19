"""URL patterns for the bookings app.

The flow is just:
  dashboard /                -> upcoming + past bookings
  new/                       -> schedule a session (pick type + slot)
  <pk>/confirmation/         -> post-booking confirmation page
  <pk>/cancel/               -> cancel a future booking
"""
from django.urls import path

from .views import (
    DashboardView,
    BookingCreateView,
    BookingConfirmationView,
    BookingCancelView,
    ScheduleView,
)

app_name = 'bookings'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('new/', ScheduleView.as_view(), name='schedule'),
    path('new/<int:slot_id>/', BookingCreateView.as_view(), name='new'),
    path('<int:pk>/confirmation/', BookingConfirmationView.as_view(), name='confirmation'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='cancel'),
]
