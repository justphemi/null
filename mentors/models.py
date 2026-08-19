"""Models for the mentors app.

MentorshipPlan   — a product (1-on-1, Group, Signal Subscription)
Mentor           — a person who delivers mentorship
TimeSlot         — a mentor's available session window
Signal           — a trading signal visible only to active subscribers
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone


class MentorshipPlan(models.Model):
    """A subscription or coaching package that customers can buy."""

    name = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    duration_days = models.PositiveIntegerField(
        help_text='How many days the plan is valid after purchase.'
    )
    sessions_included = models.PositiveIntegerField(
        default=0,
        help_text='Number of mentoring sessions included (0 for signal-only plans).'
    )

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f'{self.name} (₦{self.price})'


class Mentor(models.Model):
    """A mentor who runs sessions and posts signals."""

    class Specialization(models.TextChoices):
        FOREX = 'Forex', 'Forex'
        CRYPTO = 'Crypto', 'Crypto'
        INDICES = 'Indices', 'Indices'

    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    specialization = models.CharField(
        max_length=20,
        choices=Specialization.choices,
        default=Specialization.FOREX,
    )
    photo_url = models.URLField(blank=True)
    # Mentor can be associated with one or more plans (e.g. a plan covering multiple mentors).
    plans = models.ManyToManyField(MentorshipPlan, related_name='mentors', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """An open bookable window on a mentor's calendar."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        FULL = 'full', 'Full'
        CANCELLED = 'cancelled', 'Cancelled'

    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    capacity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Time slot'
        verbose_name_plural = 'Time slots'

    def __str__(self):
        return f'{self.mentor.name} — {self.date} {self.start_time:%H:%M}'

    @property
    def seats_taken(self):
        """How many confirmed bookings this slot has."""
        return self.bookings.filter(status__in=['pending', 'confirmed']).count()

    @property
    def seats_left(self):
        return max(self.capacity - self.seats_taken, 0)

    @property
    def is_bookable(self):
        return self.status == self.Status.OPEN and self.seats_left > 0


class Signal(models.Model):
    """A trading signal posted by a mentor."""

    class Direction(models.TextChoices):
        BUY = 'Buy', 'Buy'
        SELL = 'Sell', 'Sell'

    title = models.CharField(max_length=120)
    pair = models.CharField(max_length=20, help_text='e.g. EUR/USD, BTC/USD')
    direction = models.CharField(max_length=4, choices=Direction.choices)
    entry_price = models.DecimalField(max_digits=12, decimal_places=5)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5)
    take_profit = models.DecimalField(max_digits=12, decimal_places=5)
    posted_at = models.DateTimeField(default=timezone.now)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='signals')

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f'{self.pair} {self.direction} ({self.title})'
