"""Custom admin dashboard rendered at /admin/.

Shows:
  * bookings today
  * bookings this week
  * bookings by session type
  * upcoming vs past bookings
"""
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from .models import Booking


@staff_member_required
def admin_dashboard_view(request):
    """Replace the default Django admin index with our own dashboard."""
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())

    all_bookings = Booking.objects.all()
    bookings_today = Booking.objects.filter(time_slot__date=today).count()
    bookings_this_week = Booking.objects.filter(
        time_slot__date__gte=week_start,
        time_slot__date__lt=week_start + timedelta(days=7),
    ).count()

    recent_bookings = (
        Booking.objects
        .select_related('user', 'time_slot')
        .order_by('-created_at')[:10]
    )

    breakdown = {
        st: Booking.objects.filter(session_type=st).count()
        for st, _ in Booking.SessionType.choices
    }

    context = {
        'title': 'CybergateFX Admin',
        'bookings_today': bookings_today,
        'bookings_this_week': bookings_this_week,
        'total_bookings': all_bookings.count(),
        'breakdown': breakdown,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/dashboard.html', context)
