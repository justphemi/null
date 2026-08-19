"""Views for the booking flow.

The booking flow is intentionally small:

  /bookings/new/             -> pick an open slot (admin-set availability)
  /bookings/new/<slot_id>/   -> pick session type + confirm
  /bookings/<pk>/confirm/    -> confirmation page
  /bookings/<pk>/cancel/     -> cancel a future booking

Only future, open slots are bookable. Past slots still appear in the
dashboard as past sessions (read-only) so history is preserved.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView,
)

from mentors.models import TimeSlot

from .forms import BookingForm
from .models import Booking


def _today():
    """Local-date helper, kept here so the rest of the module is self-contained."""
    return timezone.localdate()


class DashboardView(LoginRequiredMixin, ListView):
    """The customer's booking dashboard (upcoming + past)."""

    template_name = 'bookings/dashboard.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related('time_slot', 'payment')
            .order_by('time_slot__date', 'time_slot__start_time')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bookings = list(self.get_queryset())
        today = _today()
        ctx['upcoming'] = [b for b in bookings if b.time_slot.date >= today]
        ctx['past'] = [b for b in bookings if b.time_slot.date < today]
        return ctx


class ScheduleView(LoginRequiredMixin, ListView):
    """Pick an open slot from the admin-set schedule.

    Only future, open, non-full slots are shown — past dates are filtered out
    so the user can never accidentally land on a booking form for a date
    that's already gone.
    """

    template_name = 'bookings/schedule.html'
    context_object_name = 'slots'

    def get_queryset(self):
        today = _today()
        return (
            TimeSlot.objects
            .filter(status=TimeSlot.Status.OPEN, date__gte=today)
            .order_by('date', 'start_time')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Annotate "is_full" for the template so we can dim unusable slots.
        slots = list(ctx['slots'])
        for s in slots:
            s.is_full = s.seats_left <= 0
        ctx['slots'] = slots
        return ctx


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Step 2 — confirm slot + pick session type."""

    form_class = BookingForm
    model = Booking  # required so CreateView can build an unsaved instance
    template_name = 'bookings/booking_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.slot = get_object_or_404(
            TimeSlot.objects,
            pk=kwargs['slot_id'],
            status=TimeSlot.Status.OPEN,
        )
        # Hard guard: no bookings on past slots. Past slots are visible in
        # the dashboard, but never bookable.
        if self.slot.date < _today():
            messages.error(request, 'That date is already in the past.')
            return redirect('bookings:schedule')
        if self.slot.seats_left <= 0:
            messages.error(request, 'That time slot is full.')
            return redirect('bookings:schedule')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['slot'] = self.slot
        return ctx

    def form_valid(self, form):
        # Prevent a double-booking via a race: re-check seats left.
        if self.slot.seats_left <= 0:
            messages.error(self.request, 'That time slot just filled up.')
            return redirect('bookings:schedule')

        booking = Booking.objects.create(
            user=self.request.user,
            time_slot=self.slot,
            session_type=form.cleaned_data['session_type'],
            notes=form.cleaned_data.get('notes', ''),
            status=Booking.Status.CONFIRMED,
        )
        messages.success(self.request, 'Session booked with Josh.')
        return redirect('bookings:confirmation', pk=booking.pk)


class BookingConfirmationView(LoginRequiredMixin, DetailView):
    """Confirmation page shown right after a successful booking."""
    model = Booking
    template_name = 'bookings/confirmation.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BookingCancelView(LoginRequiredMixin, UpdateView):
    """Cancel a future booking. Past bookings can't be cancelled."""

    model = Booking
    fields = []
    template_name = 'bookings/cancel.html'
    success_url = reverse_lazy('bookings:dashboard')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        booking = self.get_object() if hasattr(self, 'get_object') else None
        # Use standard dispatch for the form-submission POST; pre-flight check
        # only on GET.
        if request.method == 'GET':
            obj = get_object_or_404(Booking, pk=kwargs['pk'], user=request.user)
            if obj.time_slot.date < _today():
                messages.error(request, "Past sessions can't be cancelled.")
                return redirect('bookings:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        booking = self.get_object()
        if booking.time_slot.date < _today():
            messages.error(self.request, "Past sessions can't be cancelled.")
            return redirect('bookings:dashboard')
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.info(self.request, 'Session cancelled.')
        return redirect(self.success_url)
