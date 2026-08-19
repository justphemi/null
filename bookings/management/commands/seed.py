"""Seed the database with realistic demo content.

Usage:
    python manage.py seed

This is a tutoring-only business: customers come here to book/schedule
1-on-1 sessions with our company mentor, Josh. There are no subscription
plans and no trading signals — just a single tutoring offering priced
in Nigerian Naira (₦).

What gets created:
    - 1  Tutoring Plan  (single product, priced in Naira)
    - 1  Mentor (Josh, the company mentor)
    - 4  Time slots   (a handful of realistic upcoming availability)
    - 1  Admin user   (demo login — print at the end of the run)
    - 3  Bookings     (realistic customer activity)
"""
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, Payment
from mentors.models import MentorshipPlan, Mentor, TimeSlot

User = get_user_model()


# Naira exchange rate assumption: $1 ≈ ₦1,550 (kept realistic for 2026).
# Tutoring session is priced as a flat ₦25,000 per hour.
SESSION_PRICE_NAIRA = '25000.00'


class Command(BaseCommand):
    help = 'Populate the database with demo content (tutoring-only, prices in Naira).'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._wipe()
            plan = self._create_plan()
            josh = self._create_mentor(plan)
            slots = self._create_time_slots(josh)
            admin = self._create_admin()
            self._create_bookings(plan, josh)

        self.stdout.write(self.style.SUCCESS('\nSeed complete.\n'))
        self.stdout.write(f'  Plan:        1-on-1 Tutoring Session — ₦{SESSION_PRICE_NAIRA}')
        self.stdout.write(f'  Mentor:      {josh.name} (id={josh.pk})')
        self.stdout.write(f'  Time slots:  {slots}')
        self.stdout.write(self.style.SUCCESS('\n  Admin login:'))
        self.stdout.write('    email:    admin@cybergatefx.com')
        self.stdout.write('    password: Admin1234!\n')

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _wipe(self):
        """Clear previous demo data (keeps migrations + auth tables)."""
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        TimeSlot.objects.all().delete()
        Mentor.objects.all().delete()
        MentorshipPlan.objects.all().delete()

    def _create_plan(self):
        """A single tutoring product — no subscription tiers."""
        return MentorshipPlan.objects.create(
            name='1-on-1 Tutoring Session',
            price=SESSION_PRICE_NAIRA,
            description=(
                'A one-hour, one-on-one tutoring session with Josh — our '
                'company mentor. Bring any topic: market structure, risk '
                'management, your live trades, strategy review. Sessions '
                'are scheduled through the calendar and confirmed on payment.'
            ),
            duration_days=1,
            sessions_included=1,
        )

    def _create_mentor(self, plan):
        josh = Mentor.objects.create(
            name='Josh',
            bio=(
                "Founder and lead mentor at CybergateFX. Twelve years trading "
                "the FX, crypto and indices markets — six of them running "
                "capital for a London prop firm. Josh personally runs every "
                "tutoring session booked through the platform."
            ),
            years_experience=12,
            specialization=Mentor.Specialization.FOREX,
            photo_url='https://images.unsplash.com/photo-1560250097-0b93528c311a?w=600',
        )
        josh.plans.add(plan)
        return josh

    def _create_time_slots(self, mentor):
        """Four realistic slots — a few upcoming + one already passed,
        so the dashboard's 'upcoming / past' split is visible.
        """
        today = timezone.localdate()

        # (offset_days, start_hour, capacity)
        schedule = [
            (1, 10, 1),   # tomorrow morning
            (2, 14, 1),   # day after tomorrow, afternoon
            (4, 11, 1),   # later this week
            (-3, 9, 1),   # past slot — shows in history, not bookable
        ]

        for offset, hour, capacity in schedule:
            day = today + timedelta(days=offset)
            TimeSlot.objects.create(
                mentor=mentor,
                date=day,
                start_time=time(hour=hour, minute=0),
                duration_minutes=60,
                capacity=capacity,
                status=TimeSlot.Status.OPEN,
            )
        return len(schedule)

    def _create_admin(self):
        """Idempotent admin creation — always resets to known credentials
        so re-running `manage.py seed` always yields the same login.
        """
        admin, _ = User.objects.get_or_create(
            email='admin@cybergatefx.com',
            defaults={
                'username': 'admin@cybergatefx.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Josh',
            },
        )
        # Force the credentials and admin flags every time.
        admin.set_password('Admin1234!')
        admin.is_staff = True
        admin.is_superuser = True
        admin.username = admin.email
        admin.save()
        return admin

    def _create_bookings(self, plan, mentor):
        """Three realistic customer bookings against the seeded slots."""
        customers = [
            # email, first_name, slot_index, status
            ('chinedu.okeke@example.com',  'Chinedu',  0, Booking.Status.CONFIRMED),
            ('aisha.bello@example.com',    'Aisha',    1, Booking.Status.PENDING),
            ('tunde.adeyemi@example.com',  'Tunde',    2, Booking.Status.PENDING),
        ]

        open_slots = list(
            TimeSlot.objects.filter(status=TimeSlot.Status.OPEN)
            .order_by('date', 'start_time')
        )

        for email, first_name, slot_index, status in customers:
            if slot_index >= len(open_slots):
                continue
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': first_name},
            )
            # Always reset customer password to the demo value so re-runs
            # of `manage.py seed` produce known credentials.
            user.set_password('Demo1234!')
            user.username = user.email
            user.first_name = first_name
            user.save()

            slot = open_slots[slot_index]
            booking = Booking.objects.create(
                user=user,
                time_slot=slot,
                plan=plan,
                status=status,
                notes='',
            )

            # Confirmed bookings come with a paid payment so the
            # admin dashboard shows realistic revenue.
            payment_status = (
                Payment.Status.PAID if status == Booking.Status.CONFIRMED
                else Payment.Status.PENDING
            )
            paid_at = (
                timezone.now() if payment_status == Payment.Status.PAID else None
            )
            Payment.objects.create(
                booking=booking,
                amount=plan.price,
                method=Payment.Method.CARD,
                status=payment_status,
                paid_at=paid_at,
            )
