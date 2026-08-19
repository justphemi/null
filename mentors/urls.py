"""Public + customer-facing URLs for the mentors app."""
from django.urls import path

from .views import (
    HomeView, PlanListView, MentorListView, MentorDetailView,
    SignalFeedView, SubscriptionRequiredView,
)

app_name = 'mentors'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('plans/', PlanListView.as_view(), name='plans'),
    path('mentors/', MentorListView.as_view(), name='mentor_list'),
    path('mentors/<int:pk>/', MentorDetailView.as_view(), name='mentor_detail'),
    path('signals/', SignalFeedView.as_view(), name='signal_feed'),
    path('signals/locked/', SubscriptionRequiredView.as_view(), name='signals_locked'),
]
