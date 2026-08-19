"""Customer-facing views for the mentors app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView

from .models import MentorshipPlan, Mentor, Signal, TimeSlot


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def user_has_signal_subscription(user):
    """True if `user` currently has a paid Signal Subscription booking."""
    if not user.is_authenticated:
        return False
    # Lazy import to avoid circular import between mentors <-> bookings.
    from bookings.models import Booking
    return Booking.objects.filter(
        user=user,
        plan__name__icontains='signal',
        status__in=['confirmed', 'completed'],
        payment__status='paid',
    ).exists()


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
class HomeView(TemplateView):
    """Landing page."""
    template_name = 'mentors/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plans'] = MentorshipPlan.objects.all()[:3]
        ctx['mentors'] = Mentor.objects.all()[:3]
        ctx['latest_signals'] = Signal.objects.all()[:3]
        ctx['primary_mentor'] = Mentor.objects.first()
        return ctx


class PlanListView(ListView):
    """All mentorship plans."""
    model = MentorshipPlan
    template_name = 'mentors/plans.html'
    context_object_name = 'plans'


class MentorListView(ListView):
    """All mentors."""
    model = Mentor
    template_name = 'mentors/mentor_list.html'
    context_object_name = 'mentors'


class MentorDetailView(DetailView):
    """One mentor + their upcoming open time slots."""
    model = Mentor
    template_name = 'mentors/mentor_detail.html'
    context_object_name = 'mentor'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ctx['time_slots'] = (
            self.object.time_slots
            .filter(status='open')
            .filter(date__gte=today)
            .order_by('date', 'start_time')
        )
        return ctx


class SignalFeedView(LoginRequiredMixin, TemplateView):
    """Trading signal feed — gated by an active Signal Subscription."""
    template_name = 'mentors/signal_feed.html'

    def dispatch(self, request, *args, **kwargs):
        if not user_has_signal_subscription(request.user):
            messages.info(
                request,
                'The live signal feed is available to active Signal Subscription members only.'
            )
            return redirect('mentors:signals_locked')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['signals'] = Signal.objects.all()[:50]
        return ctx


class SubscriptionRequiredView(TemplateView):
    """Shown when a user without a subscription tries to view signals."""
    template_name = 'mentors/signals_locked.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx['signal_plan'] = MentorshipPlan.objects.filter(name__icontains='signal').first()
        except MentorshipPlan.DoesNotExist:
            ctx['signal_plan'] = None
        return ctx
