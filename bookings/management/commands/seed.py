"""Seed the database with realistic demo content.

Usage:
    python manage.py seed

Creates: Joshua (the company's owner / mentor), 3 plans, ~30 time slots,
1 admin user, 1 demo user with a confirmed Signal Subscription booking,
5 sample signals.

Real-world schedule:
    Mon - Fri   09:00 - 17:00  UTC, 60-minute slots
    Sat         10:00 - 14:00  UTC, 60-minute slots
    Sun         off
"""
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, Payment
from mentors.models import MentorshipPlan, Mentor, Signal, TimeSlot

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with demo content (single mentor schedule).'

    # --- schedule constants ------------------------------------------------
    WEEKDAY_HOURS = [(h, 60) for h in range(9, 17)]   # 09:00 - 16:00 start, 1h each
    SATURDAY_HOURS = [(h, 60) for h in range(10, 14)] # 10:00 - 13:00 start, 1h each

    def handle(self, *args, **options):
        with transaction.atomic():
            self._wipe()
            plans = self._create_plans()
            joshua = self._create_mentor(plans)
            slots_count = self._create_time_slots(joshua)
            signals_count = self._create_signals(joshua)
            admin = self._create_admin()
            demo = self._create_demo_user(plans, joshua)

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
        self.stdout.write(f'Plans:        {len(plans)}')
        self.stdout.write(f'Mentor:       {joshua.name} (id={joshua.pk})')
        self.stdout.write(f'Time slots:   {slots_count}')
        self.stdout.write(f'Signals:      {signals_count}')
        self.stdout.write(f'Admin login:  {admin.email}')
        self.stdout.write(f'Demo login:   {demo.email}')

    # --- helpers ------------------------------------------------------------
    def _wipe(self):
        """Delete existing rows (keep auth users / migrations untouched)."""
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Signal.objects.all().delete()
        TimeSlot.objects.all().delete()
        Mentor.objects.all().delete()
        MentorshipPlan.objects.all().delete()

    def _create_plans(self):
        return [
            MentorshipPlan.objects.create(
                name='1-on-1 Coaching',
                price='299.00',
                description=(
                    'Personal one-to-one coaching with Joshua. Includes a strategy '
                    'review, weekly 1:1 calls, and a customized trading plan.'
                ),
                duration_days=30,
                sessions_included=4,
            ),
            MentorshipPlan.objects.create(
                name='Group Mentorship',
                price='149.00',
                description=(
                    'Weekly group sessions with up to 12 traders. Learn to read the market, '
                    'manage risk, and build a robust trading plan together.'
                ),
                duration_days=30,
                sessions_included=8,
            ),
            MentorshipPlan.objects.create(
                name='Signal Subscription',
                price='79.00',
                description=(
                    'Live trading signals posted by Joshua across Forex, Crypto, '
                    'and Indices. Includes entry, stop-loss and take-profit levels.'
                ),
                duration_days=30,
                sessions_included=0,
            ),
        ]

    def _create_mentor(self, plans):
        joshua = Mentor.objects.create(
            name='Joshua',
            bio=(
                "Founder and lead mentor at CybergateFX. Twelve years trading the FX, "
                "crypto and indices markets — six of them running capital for a London "
                "prop firm. Joshua personally runs every 1-on-1 and group session and "
                "is the author of every signal in the live feed."
            ),
            years_experience=12,
            specialization=Mentor.Specialization.FOREX,
            photo_url='https://images.unsplash.com/photo-1560250097-0b93528c311a?w=600',
        )
        joshua.plans.set(plans)
        return joshua

    def _create_time_slots(self, mentor):
        """Build the next 4 weeks of slots following a Mon-Fri + Sat morning schedule."""
        created = 0
        today = timezone.localdate()
        horizon = today + timedelta(days=28)

        day = today
        while day <= horizon:
            weekday = day.weekday()  # 0=Mon, 6=Sun
            if weekday in (0, 1, 2, 3, 4):           # Mon-Fri
                hours = self.WEEKDAY_HOURS
            elif weekday == 5:                       # Saturday
                hours = self.SATURDAY_HOURS
            else:                                    # Sunday — day off
                day += timedelta(days=1)
                continue

            for hour, duration in hours:
                # Skip slots earlier than the current time on today.
                if day == today and hour < timezone.localtime().hour:
                    continue
                TimeSlot.objects.create(
                    mentor=mentor,
                    date=day,
                    start_time=time(hour=hour, minute=0),
                    duration_minutes=duration,
                    capacity=1,
                    status=TimeSlot.Status.OPEN,
                )
                created += 1

            day += timedelta(days=1)
        return created

    def _create_signals(self, mentor):
        signal_data = [
            ('EUR/USD Buy Setup',    'EUR/USD', Signal.Direction.BUY,  '1.08250', '1.07900', '1.09200'),
            ('XAU/USD Sell Bias',    'XAU/USD', Signal.Direction.SELL, '2340.50', '2355.00', '2300.00'),
            ('BTC Long Continuation','BTC/USD', Signal.Direction.BUY,  '67500.0', '66200.0', '70500.0'),
            ('ETH Breakout Watch',   'ETH/USD', Signal.Direction.BUY,  '3450.00', '3320.00', '3720.00'),
            ('S&P 500 Range Sell',   'US500',   Signal.Direction.SELL, '5230.00', '5260.00', '5140.00'),
        ]
        for title, pair, direction, entry, sl, tp in signal_data:
            Signal.objects.create(
                title=title, pair=pair, direction=direction,
                entry_price=entry, stop_loss=sl, take_profit=tp, mentor=mentor,
            )
        return len(signal_data)

    def _create_admin(self):
        admin, created = User.objects.get_or_create(
            email='admin@cybergatefx.com',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'username': 'admin@cybergatefx.com',
                'first_name': 'Joshua',
            },
        )
        if created:
            admin.set_password('Admin123!')
            admin.save()
        else:
            # Always reset the password so re-running seed gives a known creds.
            admin.set_password('Admin123!')
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
        return admin

    def _create_demo_user(self, plans, mentor):
        demo, created = User.objects.get_or_create(
            email='demo@cybergatefx.com',
            defaults={
                'username': 'demo@cybergatefx.com',
                'first_name': 'Demo Trader',
            },
        )
        if created:
            demo.set_password('Demo1234!')
            demo.save()
        signal_plan = next(p for p in plans if 'Signal' in p.name)
        slot = TimeSlot.objects.filter(status='open').first()
        booking = Booking.objects.create(
            user=demo,
            time_slot=slot,
            plan=signal_plan,
            status=Booking.Status.CONFIRMED,
            notes='Demo user with active subscription.',
        )
        Payment.objects.create(
            booking=booking,
            amount=signal_plan.price,
            method=Payment.Method.CARD,
            status=Payment.Status.PAID,
            paid_at=timezone.now(),
        )
        return demo
