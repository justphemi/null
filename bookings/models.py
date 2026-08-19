"""Booking and Payment models.

A booking is one user, one time slot, one plan. Each booking has at most
one payment record (one-to-one).
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from mentors.models import MentorshipPlan, TimeSlot


class Booking(models.Model):
    """A user's booking of a single time slot under a specific plan."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    plan = models.ForeignKey(
        MentorshipPlan,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.user.email} — {self.time_slot}'

    @property
    def is_past(self):
        """True once the slot's date is in the past."""
        from django.utils import timezone
        return self.time_slot.date < timezone.localdate()


class Payment(models.Model):
    """A single payment attached to a booking (one-to-one)."""

    class Method(models.TextChoices):
        CARD = 'card', 'Card'
        BANK = 'bank', 'Bank transfer'
        WALLET = 'wallet', 'Wallet'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(
        max_length=10,
        choices=Method.choices,
        default=Method.CARD,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.booking_id} {self.amount} {self.status}'
