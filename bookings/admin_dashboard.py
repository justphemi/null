"""Custom admin dashboard rendered at /admin/.

Shows:
  * bookings today
  * bookings this week
  * pending payments + outstanding amount
  * active signal subscribers
  * most recent bookings
"""
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from .models import Booking, Payment


@staff_member_required
def admin_dashboard_view(request):
    """Replace the default Django admin index with our own dashboard."""
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())

    bookings_today = Booking.objects.filter(time_slot__date=today).count()
    bookings_this_week = Booking.objects.filter(
        time_slot__date__gte=week_start,
        time_slot__date__lt=week_start + timedelta(days=7),
    ).count()
    total_bookings = Booking.objects.count()

    pending_payments = Payment.objects.filter(status=Payment.Status.PENDING)
    pending_payments_count = pending_payments.count()
    pending_payments_total = sum(p.amount for p in pending_payments)

    # A "subscriber" is a booking whose plan contains "signal" and whose
    # payment is paid. Matches the rule used by SignalFeedView.
    active_subscriptions = (
        Booking.objects
        .filter(
            plan__name__icontains='signal',
            status__in=[Booking.Status.CONFIRMED, Booking.Status.COMPLETED],
            payment__status=Payment.Status.PAID,
        )
        .count()
    )

    recent_bookings = (
        Booking.objects
        .select_related('user', 'time_slot')
        .order_by('-created_at')[:10]
    )

    context = {
        'title': 'CybergateFX Admin',
        'bookings_today': bookings_today,
        'bookings_this_week': bookings_this_week,
        'total_bookings': total_bookings,
        'pending_payments_count': pending_payments_count,
        'pending_payments_total': pending_payments_total,
        'active_subscriptions': active_subscriptions,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/dashboard.html', context)
