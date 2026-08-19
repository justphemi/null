# CybergateFX &mdash; User Story

## Project context

**CybergateFX** is a Django web app that lets retail traders buy forex
trading signals and mentorship sessions from a single senior mentor
(Joshua). Customers browse plans, book a time slot, pay (via a
simulated checkout), and either attend a coaching session or follow a
live trading-signal feed.

This document captures the *who*, the *what* and the *why* of the
system from the user's perspective. It is the first deliverable in the
analysis phase, followed by the use case, sequence and class diagrams.

---

## 1. Personas

| Persona       | Who they are                                                              | Primary goal                                                |
|---------------|---------------------------------------------------------------------------|-------------------------------------------------------------|
| **Customer**  | A retail trader looking for guidance, structure and live trading calls.   | Buy a plan, book a session and follow the signal feed.      |
| **Mentor**    | Joshua, the founder / lead mentor. Runs every session and posts every signal. | Sell coaching time and signal access through the platform.   |
| **Admin**     | A staff member running the business.                                       | Operate the platform &mdash; post signals, manage slots, verify payments. |
| **Visitor**   | Someone who has heard about the product but has not signed up.             | Decide whether CybergateFX is worth signing up for.          |

---

## 2. Primary user stories

The stories are written in the standard *As a / I want / so that* format
and prioritized into three releases.

### MVP (Release 1)

1. **Sign up**
   *As a visitor, I want to create an account with my name, email and
   password, so that I can buy a plan and book sessions.*

2. **Log in / log out**
   *As a returning customer, I want to log in by email and log out when
   I'm done, so that my dashboard stays private.*

3. **Browse plans**
   *As a visitor, I want to see the three available plans (1-on-1, Group,
   Signal Subscription) with prices and what they include, so that I can
   pick the right one.*

4. **Browse mentor and schedule**
   *As a visitor, I want to see the mentor's profile and the open time
   slots in their weekly schedule, so that I can pick a session.*

5. **Book a session**
   *As a customer, I want to book one of the mentor's open slots under a
   chosen plan, so that the slot is reserved for me.*

6. **Simulated payment**
   *As a customer, I want to complete a (clearly marked simulated)
   checkout, so that my booking becomes confirmed.*

7. **Booking confirmation**
   *As a customer, I want a confirmation page with all the details of
   my booking, so that I have a receipt.*

8. **Customer dashboard**
   *As a customer, I want to see my upcoming and past bookings in one
   place, so that I can manage my schedule.*

9. **Cancel a booking**
   *As a customer, I want to cancel an upcoming booking, so that my
   payment is marked as refunded and the slot is freed up.*

### Release 2 &mdash; signals

10. **Live signal feed**
    *As a Signal Subscriber, I want to see live trading signals posted by
    the mentor (entry, SL, TP), so that I can act on them.*

11. **Subscription gating**
    *As a customer who has not bought the Signal Subscription plan, I want
    to be told that the feed is locked and shown how to subscribe, so
    that I understand how to unlock it.*

### Release 3 &mdash; admin

12. **Admin dashboard**
    *As an admin, I want to see bookings today, bookings this week,
    pending payments and active subscriber count on the admin home page,
    so that I can monitor the business at a glance.*

13. **Manage mentor and slots**
    *As an admin, I want to edit the mentor and add or edit their time
    slots in one screen, so that scheduling is fast.*

14. **Post signals from admin**
    *As an admin (acting on behalf of the mentor), I want to post new
    signals directly from the Django admin, so that subscribers see them
    immediately.*

---

## 3. Acceptance criteria (per MVP story)

The MVP is *done* when every story below passes its acceptance check on
the running app.

### 3.1 Sign up
- `/accounts/signup/` renders a form with **Full name**, **Email**,
  **Password**, **Confirm password** fields.
- After successful submission, the user is logged in and redirected to
  the dashboard.
- Submitting an email that already exists shows an inline error and does
  **not** create a duplicate account.

### 3.2 Browse plans
- `/plans/` lists all three plans with price, description, sessions
  included, and duration.
- A visitor who is not logged in sees a **Sign up to start** button on
  each card.

### 3.3 Browse mentor and schedule
- `/mentors/` shows the single mentor (Joshua) and links to his
  profile.
- `/mentors/<id>/` lists only **upcoming** open slots from today
  onwards, ordered by date and start time.
- A "Weekly schedule" callout shows Mon&ndash;Fri 09:00&ndash;17:00,
  Saturday 10:00&ndash;14:00, Sunday day off.

### 3.4 Book a session
- Clicking **Book** on a slot takes an authenticated customer to
  `/bookings/new/<slot_id>/`.
- The form pre-selects the chosen slot and lets the customer choose a
  plan and (optionally) add notes.
- Submitting creates a Booking (status=PENDING) plus a Payment
  (status=PENDING), and redirects to the payment page.

### 3.5 Simulated payment
- The payment page shows a yellow banner: *"This is a demo environment.
  No real payment is taken."*
- Submitting the form calls `Payment.mark_paid()`, sets the booking to
  CONFIRMED, sets the payment to PAID with `paid_at = now`, and
  redirects to `/bookings/<id>/confirmation/`.

### 3.6 Booking confirmation
- The confirmation page shows: booking id, mentor, date &amp; time,
  plan, status (Confirmed), payment (Paid, simulated).

### 3.7 Customer dashboard
- `/bookings/dashboard/` shows two tables &mdash; *Upcoming sessions*
  and *Past sessions* &mdash; and three stat tiles (Upcoming count,
  Past count, Total).

### 3.8 Cancel a booking
- *Cancel* on an upcoming booking posts to `/bookings/<id>/cancel/`,
  shows a confirmation page; submitting sets status=CANCELLED, marks
  the payment REFUNDED and returns to the dashboard.

### 3.9 Live signal feed
- A user with at least one paid **Signal Subscription** booking can
  view `/signals/` and sees the most recent 50 signals.
- A user without such a booking is redirected to `/signals/locked/`,
  which explains the plan and links to `/plans/`.

### 3.10 Admin dashboard
- After logging in via `/admin/portal/`, an admin who visits `/admin/`
  sees four KPI tiles: Bookings today, Bookings this week, Pending
  payments (count + dollar total), Active signal subscribers. Below
  them, quick links and a *Recent bookings* table.

### 3.11 Manage mentor and slots
- The mentor admin page (`/admin/portal/mentors/mentor/`) shows a
  `TimeSlotInline` so new slots can be added without leaving the page.
- `list_editable = ('status',)` on the TimeSlot admin lets the admin
  flip a slot to FULL or CANCELLED in bulk.
- `list_filter`, `search_fields` and `list_display` are set on every
  model.

### 3.12 Post signals from admin
- `/admin/portal/mentors/signal/add/` is reachable by an admin and
  accepts a new signal with `title, pair, direction, entry_price,
  stop_loss, take_profit, mentor`. After saving, it appears immediately
  on `/signals/` for subscribers.

---

## 4. Non-functional requirements

| Area        | Requirement                                                                                  |
|-------------|----------------------------------------------------------------------------------------------|
| Security    | Passwords are hashed with Django's default PBKDF2. CSRF tokens on every POST.                  |
| Performance | All list pages paginate implicitly through Django ORM; no N+1 queries on dashboard or feed.   |
| Availability| Runs on Render's free tier (gunicorn + Postgres). SQLite is used locally.                    |
| i18n        | All copy is in English; templates leave room for translation later (no inline strings).       |
| Reliability | A failed simulated payment does not crash the server &mdash; it shows form errors.            |
| Maintainability | Code is split into three apps (`accounts`, `mentors`, `bookings`). Class-based views with clear docstrings. |

---

## 5. Out of scope (this version)

- Real payment gateway integration (Stripe / PayPal).
- Real-time price feeds from a broker API.
- Multi-mentor support.
- Email notifications (e.g. "your session is tomorrow").
- Calendar (.ics) export.
- Reviews / ratings of mentors.
