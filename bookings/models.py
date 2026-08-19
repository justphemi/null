"""Booking model.

A booking is one user, one slot, one session type. There are no plans,
no mentor detail pages — the user just picks a type when they book and
the slot comes from the admin-set availability.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from mentors.models import TimeSlot


class Booking(models.Model):
    """A user's booking of a single time slot with Josh."""

    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class SessionType(models.TextChoices):
        COACHING = 'coaching', '1-on-1 Coaching'
        GROUP = 'group', 'Group Session'
        SIGNAL = 'signal', 'Signal Session'

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
    session_type = models.CharField(
        max_length=12,
        choices=SessionType.choices,
        default=SessionType.COACHING,
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.CONFIRMED,
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
