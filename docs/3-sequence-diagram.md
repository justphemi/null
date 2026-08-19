# CybergateFX &mdash; Sequence Diagrams &amp; Descriptions

Sequence diagrams focus on the *time-ordered message flow* between the
actors, the view layer, Django's URL/middleware stack, the ORM/models
and the database. Three key scenarios are covered:

1. **Sign up &rarr; auto-login** (UC-01)
2. **Browse &rarr; book &rarr; pay &rarr; confirmation** (UC-04, UC-05, UC-06, UC-07)
3. **Live signal feed with subscription gating** (UC-10, UC-11)

Diagrams are in Mermaid so they render natively on GitHub, GitLab and
most Markdown viewers. A textual trace that reads top-to-bottom follows
each diagram.

---

## 3.1 Sign up &rarr; auto-login

### Diagram

```mermaid
%%{init: {'theme':'light', 'sequence': {'mirrorActors':false}}}%%
sequenceDiagram
  autonumber
  actor Visitor as V
  participant Browser as Browser
  participant SignupView as SignupView<br/>(accounts.views)
  participant SignupForm as SignupForm
  participant UserManager as UserManager
  participant DB as SQLite / Postgres
  participant Auth as django.contrib.auth

  V->>Browser: GET /accounts/signup/
  Browser->>SignupView: GET
  SignupView->>Browser: 200 (form, csrf token)
  V->>Browser: submit (name, email, password1, password2)
  Browser->>SignupView: POST
  SignupView->>SignupForm: form.is_valid()
  SignupForm-->>SignupView: cleaned data (or errors)
  SignupView->>UserManager: create_user(email, password, first_name=name)
  UserManager->>DB: INSERT accounts_user
  DB-->>UserManager: ok
  UserManager-->>SignupView: new User
  SignupView->>Auth: login(request, user)
  Auth->>Browser: Set-Cookie: sessionid=...
  SignupView-->>Browser: 302 -> /bookings/dashboard/
```

### Step-by-step description

1. The visitor opens the signup page in the browser. Django's
   `CsrfViewMiddleware` injects a token into the rendered form.
2. The visitor fills in **Full name**, **Email**, **Password**,
   **Confirm password** and submits.
3. `SignupView` (a class-based `CreateView`) delegates validation to
   `SignupForm`. The form checks that the email is unique and that
   both passwords match (Django's `UserCreationForm` does the heavy
   lifting).
4. On valid input, `SignupForm.save()` calls
   `UserManager._create_user`, which normalizes the email, sets
   `username = email`, hashes the password with PBKDF2, and inserts a
   new row into `accounts_user`.
5. `SignupView` then calls `django.contrib.auth.login()`, which writes a
   session row and tells the browser to set the `sessionid` cookie.
6. Finally the view returns `302 Location: /bookings/dashboard/`. The
   browser follows the redirect and the customer sees their dashboard.

### Why this matters

- The signup view is *transactional*: if either the `INSERT` or the
  `login()` step fails, no user appears in the database and the
  customer is shown an error.
- Because the user is logged in *during* the response cycle, the very
  first page they see after signing up is the dashboard &mdash; no
  extra click.

---

## 3.2 Browse &rarr; book &rarr; pay &rarr; confirmation

This is the longest end-to-end flow in the app and is split into three
sub-flows so the diagram stays readable.

### Sub-flow A &mdash; browse mentor + slot list

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Customer as C
  participant Browser
  participant MentorDetail as MentorDetailView<br/>(mentors.views)
  participant Mentor as Mentor (ORM)
  participant TimeSlot as TimeSlot (ORM)
  participant DB

  C->>Browser: GET /mentors/<id>/
  Browser->>MentorDetail: GET
  MentorDetail->>Mentor: Mentor.objects.get(pk=id)
  Mentor->>DB: SELECT * FROM mentors_mentor WHERE id = ?
  DB-->>Mentor: row
  Mentor-->>MentorDetail: Mentor instance
  MentorDetail->>TimeSlot: mentor.time_slots.filter(status='open', date__gte=today).order_by(...)
  TimeSlot->>DB: SELECT * FROM mentors_timeslot WHERE mentor_id = ? AND ...
  DB-->>TimeSlot: N rows
  TimeSlot-->>MentorDetail: queryset
  MentorDetail-->>Browser: 200 (mentor.html, slots list)
```

### Sub-flow B &mdash; book a session

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Customer as C
  participant Browser
  participant BookingCreate as BookingCreateView<br/>(bookings.views)
  participant BookingForm
  participant Booking as Booking (ORM)
  participant Payment as Payment (ORM)
  participant DB

  C->>Browser: POST /bookings/new/<slot_id>/
  Browser->>BookingCreate: POST (plan, time_slot, notes)
  BookingCreate->>BookingForm: form.is_valid()
  BookingForm-->>BookingCreate: cleaned data
  BookingCreate->>BookingCreate: assert slot is future & has seats
  BookingCreate->>DB: BEGIN
  BookingCreate->>Booking: Booking.objects.create(user, slot, plan, notes, PENDING)
  Booking->>DB: INSERT bookings_booking
  DB-->>Booking: id
  BookingCreate->>Payment: Payment.objects.create(booking, amount=plan.price, PENDING)
  Payment->>DB: INSERT bookings_payment
  DB-->>Payment: id
  BookingCreate->>DB: COMMIT
  BookingCreate-->>Browser: 302 -> /bookings/<booking_id>/pay/
```

### Sub-flow C &mdash; simulated pay &rarr; confirmation

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Customer as C
  participant Browser
  participant PaymentView as PaymentView<br/>(bookings.views)
  participant SimulatedForm as SimulatedPaymentForm
  participant Payment as Payment (ORM)
  participant Booking as Booking (ORM)
  participant Confirmation as BookingConfirmationView
  participant DB

  C->>Browser: POST /bookings/<id>/pay/
  Browser->>PaymentView: POST (method, card_*)
  PaymentView->>SimulatedForm: form.is_valid()
  SimulatedForm-->>PaymentView: cleaned data
  PaymentView->>Payment: payment.mark_paid()
  Payment->>DB: UPDATE bookings_payment SET status='paid', paid_at=now WHERE id=?
  PaymentView->>Booking: booking.status = CONFIRMED; booking.save()
  Booking->>DB: UPDATE bookings_booking SET status='confirmed' WHERE id=?
  PaymentView-->>Browser: 302 -> /bookings/<id>/confirmation/
  C->>Browser: GET /bookings/<id>/confirmation/
  Browser->>Confirmation: GET
  Confirmation->>DB: SELECT booking + payment JOIN
  DB-->>Confirmation: row
  Confirmation-->>Browser: 200 (confirmation.html)
```

### Step-by-step description

- **Browse**: `MentorDetailView.get_context_data` runs two ORM queries
  &mdash; one for the mentor, one for `time_slots` &mdash; both using
  indexed lookups by primary key and the `mentor_id` foreign key.
- **Book**: `BookingCreateView` wraps the booking and payment creation
  in a `transaction.atomic()` block so we never end up with a booking
  but no payment (or vice versa). On success the customer is sent to
  the payment page for the freshly created booking.
- **Pay**: `PaymentView` calls `Payment.mark_paid()` (a model method
  that sets `status='paid'` and `paid_at=now()`) and flips the booking
  to `CONFIRMED`. Both rows are updated in two `UPDATE` statements.
- **Confirmation**: A simple read-only `DetailView` joins the booking
  and the related payment and renders the final receipt.

### Why this matters

- The booking step uses an atomic transaction, so a crash or error
  between "create booking" and "create payment" rolls back both
  inserts.
- Payment is a `OneToOneField` &mdash; the schema guarantees there is
  never more than one payment per booking.
- The simulated checkout never touches a real gateway; the *only*
  effect is two SQL `UPDATE` statements on the local DB.

---

## 3.3 Live signal feed (with subscription gating)

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Customer as C
  participant Browser
  participant SignalFeedView as SignalFeedView<br/>(mentors.views)
  participant Helpers as user_has_signal_subscription
  participant Booking as Booking (ORM)
  participant Payment as Payment (ORM)
  participant DB

  C->>Browser: GET /signals/
  Browser->>SignalFeedView: GET
  SignalFeedView->>Helpers: user_has_signal_subscription(request.user)
  Helpers->>Booking: Booking.objects.filter(user, plan__name~'signal', status in (CONFIRMED, COMPLETED), payment__status='paid').exists()
  Booking->>DB: SELECT 1 FROM bookings_booking b JOIN mentors_mentorshipplan p ON b.plan_id=p.id JOIN bookings_payment pay ON pay.booking_id=b.id WHERE ...
  DB-->>Booking: bool
  Booking-->>Helpers: True / False
  Helpers-->>SignalFeedView: True / False

  alt has active subscription
    SignalFeedView->>DB: SELECT * FROM mentors_signal ORDER BY posted_at DESC LIMIT 50
    DB-->>SignalFeedView: rows
    SignalFeedView-->>Browser: 200 (signal_feed.html)
  else no active subscription
    SignalFeedView-->>Browser: 302 -> /signals/locked/
    C->>Browser: GET /signals/locked/
    Browser-->>C: 200 (signals_locked.html)
  end
```

### Step-by-step description

1. The customer requests `/signals/`. Because this is a
   `LoginRequiredMixin`-protected view, anonymous visitors are already
   redirected to `/accounts/login/`.
2. `SignalFeedView.dispatch` calls the helper
   `user_has_signal_subscription(user)`. The helper runs a single SQL
   query that joins `bookings_booking` &rarr; `mentors_mentorshipplan`
   &rarr; `bookings_payment` and returns whether at least one row
   matches.
3. If the helper returns `True`, the view runs a second query for the
   50 most recent signals and renders `signal_feed.html`.
4. If the helper returns `False`, the view returns a 302 to
   `/signals/locked/`, where the customer is shown a callout with the
   Signal Subscription plan and a *View plans* button.

### Why this matters

- Gating is done at *query time*, not at template time. There is no way
  for a forbidden signal to leak into the HTML response.
- The helper uses `__` lookups to join through the ORM, so the query is
  a single SQL statement &mdash; no Python-level loops over bookings.

---

## 3.4 Cancel a booking (for completeness)

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Customer as C
  participant Browser
  participant BookingCancel as BookingCancelView<br/>(bookings.views)
  participant Booking as Booking (ORM)
  participant Payment as Payment (ORM)
  participant DB

  C->>Browser: GET /bookings/<id>/cancel/
  Browser->>BookingCancel: GET
  BookingCancel->>DB: SELECT booking WHERE id=? AND user=?
  DB-->>BookingCancel: row
  BookingCancel-->>Browser: 200 (cancel.html)
  C->>Browser: POST /bookings/<id>/cancel/
  Browser->>BookingCancel: POST
  BookingCancel->>Booking: status='cancelled'; save()
  Booking->>DB: UPDATE bookings_booking
  BookingCancel->>Payment: status='refunded'; save()
  Payment->>DB: UPDATE bookings_payment
  BookingCancel-->>Browser: 302 -> /bookings/dashboard/
```

The cancel flow is intentionally short: two updates, one redirect. It
re-uses the same `Booking.objects.filter(user=...)` guard that the
payment and confirmation views use, so a customer cannot cancel another
customer's booking.

---

## 3.5 Admin dashboard

```mermaid
%%{init: {'theme':'light'}}%%
sequenceDiagram
  autonumber
  actor Admin as A
  participant Browser
  participant AdminDashboard as admin_dashboard_view<br/>(bookings.admin_dashboard)
  participant Booking as Booking (ORM)
  participant Payment as Payment (ORM)
  participant DB

  A->>Browser: GET /admin/
  Browser->>AdminDashboard: GET (staff_member_required)
  AdminDashboard->>Booking: count(today) + count(this_week)
  Booking->>DB: SELECT COUNT(*) ...
  AdminDashboard->>Payment: count + sum where status='pending'
  Payment->>DB: SELECT COUNT(*), SUM(amount) ...
  AdminDashboard->>Booking: count active signal subscriptions
  Booking->>DB: SELECT COUNT(*) ... (paid + signal plan)
  AdminDashboard-->>Browser: 200 (admin/dashboard.html)
```

A single HTTP roundtrip, four `COUNT`/`SUM` queries, one render. There
is no caching, but the dashboard is staff-only and the data is bounded
by the size of the bookings table, so query cost is negligible.
