# CybergateFX &mdash; Use Case Diagram &amp; Descriptions

## 1. Use case diagram

The diagram is in Mermaid and renders natively on GitHub, GitLab and any
Markdown viewer that supports Mermaid (e.g. the VS Code Markdown
preview). For tools that don't, the textual description that follows
captures the same information.

```mermaid
%%{init: {'theme':'light', 'themeVariables': {'fontSize':'14px'}}}%%
left to right direction
actor "Visitor" as V
actor "Customer (Trader)" as C
actor "Admin (Staff)" as A
actor "Mentor (Joshua)" as M

rectangle "CybergateFX" {
  usecase "UC-01 Sign up"              as UC01
  usecase "UC-02 Log in / log out"     as UC02
  usecase "UC-03 Browse plans"         as UC03
  usecase "UC-04 Browse mentor and schedule" as UC04
  usecase "UC-05 Book a session"       as UC05
  usecase "UC-06 Pay (simulated)"      as UC06
  usecase "UC-07 View booking confirmation" as UC07
  usecase "UC-08 View customer dashboard"   as UC08
  usecase "UC-09 Cancel a booking"     as UC09
  usecase "UC-10 View live signal feed" as UC10
  usecase "UC-11 View subscription-locked page" as UC11
  usecase "UC-12 View admin dashboard" as UC12
  usecase "UC-13 Manage mentor and time slots" as UC13
  usecase "UC-14 Post a new signal"    as UC14
  usecase "UC-15 Verify payment"       as UC15
  usecase "UC-16 Log out"              as UC16
}

V -- UC01
V -- UC02
V -- UC03
V -- UC04
C -- UC03
C -- UC04
C -- UC05
C -- UC06
C -- UC07
C -- UC08
C -- UC09
C -- UC10
C -- UC11
C -- UC16
A -- UC02
A -- UC12
A -- UC13
A -- UC14
A -- UC15
M -- UC14
```

The dashed arrow from Mentor &rarr; UC-14 is implicit in the model: in
practice, the admin posts signals on the mentor's behalf from the
admin portal.

---

## 2. Actor descriptions

| Actor                | Description                                                                                                                |
|----------------------|----------------------------------------------------------------------------------------------------------------------------|
| **Visitor**          | An unauthenticated user who is exploring the public pages (`/`, `/plans/`, `/mentors/`, `/mentors/<id>/`).                  |
| **Customer (Trader)**| An authenticated user who has signed up and can book sessions, pay (simulated), manage bookings and view signals (if subscribed). |
| **Mentor (Joshua)**  | The single mentor who owns the platform. In the system he is represented as a `Mentor` row; all sessions and signals are attributed to him. |
| **Admin (Staff)**    | A `User` with `is_staff = True` who can access `/admin/portal/` and the custom `/admin/` dashboard.                          |

---

## 3. Use case descriptions

The format follows the standard Cockburn template: *actor*, *trigger*,
*preconditions*, *postconditions*, *main flow*, *alternative flows*,
*exceptions*.

### UC-01 &mdash; Sign up

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Visitor                                                                                            |
| Goal             | Create a new account and be logged in.                                                             |
| Trigger          | User clicks *Get started* in the navbar or *Sign up to start* on a plan card.                      |
| Preconditions    | None.                                                                                              |
| Postconditions   | A new `User` row exists. The visitor is logged in and redirected to the dashboard.                 |
| Main flow        | 1. Visitor opens `/accounts/signup/`. <br>2. Submits form with **Full name**, **Email**, **Password**, **Confirm password**. <br>3. System validates input, ensures email is unique, creates the user with `username = email`, and logs them in. |
| Alternative flow | If email already exists &mdash; system shows an inline error and does not create the user.         |
| Exceptions       | If passwords don't match &mdash; show Django's default validation errors.                          |

### UC-02 &mdash; Log in

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Visitor or Admin                                                                                   |
| Goal             | Authenticate and start a session.                                                                  |
| Trigger          | User clicks *Log in* in the navbar.                                                                |
| Preconditions    | Account exists.                                                                                    |
| Postconditions   | A session cookie is set; user is redirected to `/bookings/dashboard/` (admin goes to `/admin/portal/`). |
| Main flow        | 1. Open `/accounts/login/`. <br>2. Submit email + password. <br>3. `AuthenticationForm` validates; user is logged in. |
| Exceptions       | Bad credentials &mdash; show a non-field error.                                                    |

### UC-04 &mdash; Browse mentor and schedule

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Visitor or Customer                                                                                |
| Goal             | View the mentor's profile and the list of upcoming open slots.                                      |
| Preconditions    | At least one open slot exists.                                                                     |
| Postconditions   | None &mdash; read-only view.                                                                       |
| Main flow        | 1. Open `/mentors/`. <br>2. Open `/mentors/<id>/`. <br>3. View shows bio, plans covered, weekly schedule callout and a list of upcoming open slots. |
| Notes            | The list is filtered to `status='open' AND date >= today` and ordered by date + start time.         |

### UC-05 &mdash; Book a session

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer                                                                                           |
| Goal             | Reserve an open slot under a chosen plan.                                                           |
| Trigger          | Click *Book* on a slot in the mentor's schedule.                                                   |
| Preconditions    | Customer is authenticated, slot is open, slot is in the future, slot has at least one free seat.    |
| Postconditions   | A new `Booking` (status=PENDING) and a related `Payment` (status=PENDING) are created.             |
| Main flow        | 1. GET `/bookings/new/<slot_id>/` shows a form pre-selecting the slot. <br>2. Customer picks a plan and optional notes. <br>3. POST creates booking &amp; payment, redirects to `/bookings/<id>/pay/`. |
| Exceptions       | Slot no longer available &mdash; redirect back to mentor profile with an error message.            |

### UC-06 &mdash; Pay (simulated)

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer                                                                                           |
| Goal             | Confirm the booking via the simulated checkout.                                                    |
| Trigger          | Submission of `/bookings/<id>/pay/`.                                                               |
| Preconditions    | Booking and Payment exist for the user; Payment is in PENDING state.                                |
| Postconditions   | Payment is PAID (`paid_at = now`); Booking is CONFIRMED.                                           |
| Main flow        | 1. Page shows booking summary + a yellow "simulated" banner. <br>2. Customer submits method + (if card) card fields. <br>3. View calls `Payment.mark_paid()`, sets `Booking.status = CONFIRMED`, redirects to confirmation. |
| Exceptions       | Missing card fields &mdash; show form errors and do not confirm.                                    |

### UC-07 &mdash; View booking confirmation

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer                                                                                           |
| Goal             | See a final receipt for a confirmed booking.                                                        |
| Trigger          | Redirect after successful payment.                                                                 |
| Main flow        | Renders booking id, mentor, date &amp; time, plan, status badge (Confirmed), payment badge (Paid, simulated). |

### UC-08 &mdash; View customer dashboard

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer                                                                                           |
| Goal             | See upcoming and past bookings in one screen.                                                      |
| Trigger          | Login redirect, or click *Dashboard* in the navbar.                                                |
| Main flow        | 1. View lists the customer's bookings. <br>2. Splits them into *Upcoming* (`date >= today`) and *Past* (`date < today`). <br>3. Shows three stat tiles. |
| Notes            | Each upcoming row has a *Cancel* action; past rows do not.                                         |

### UC-09 &mdash; Cancel a booking

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer                                                                                           |
| Goal             | Cancel an upcoming booking and mark its payment as refunded.                                       |
| Trigger          | Click *Cancel* on an upcoming booking row in the dashboard.                                        |
| Preconditions    | Booking belongs to the user; booking is upcoming.                                                  |
| Postconditions   | Booking.status = CANCELLED; Payment.status = REFUNDED.                                             |
| Main flow        | 1. GET `/bookings/<id>/cancel/` shows a confirmation page. <br>2. POST cancels the booking and redirects to the dashboard with an info message. |

### UC-10 &mdash; View live signal feed

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer (Signal Subscriber)                                                                       |
| Goal             | See the latest trading signals posted by Joshua.                                                   |
| Preconditions    | User has at least one booking with `plan.name ilike '%signal%'`, `status in (CONFIRMED, COMPLETED)` and `payment.status = PAID`. |
| Main flow        | `/signals/` renders the 50 most recent signals with pair, direction (Buy/Sell pill), entry, stop-loss, take-profit, mentor and posted-at timestamp. |

### UC-11 &mdash; View subscription-locked page

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer (without an active Signal Subscription)                                                   |
| Goal             | Tell the customer the feed is locked and show how to subscribe.                                    |
| Trigger          | A non-subscriber visits `/signals/`.                                                               |
| Main flow        | Redirected to `/signals/locked/`, which shows the Signal Subscription plan card and *View plans* / *Browse mentors* buttons. |

### UC-12 &mdash; View admin dashboard

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Admin                                                                                              |
| Goal             | See operational KPIs at a glance.                                                                  |
| Preconditions    | Logged-in staff user.                                                                              |
| Main flow        | `/admin/` renders four stat tiles (Bookings today, Bookings this week, Pending payments count + total, Active signal subscribers), quick links to each admin section, and a *Recent bookings* table. |

### UC-13 &mdash; Manage mentor and time slots

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Admin                                                                                              |
| Goal             | Update mentor profile and add/edit time slots in one screen.                                       |
| Main flow        | `/admin/portal/mentors/mentor/` renders the mentor edit page with a `TimeSlotInline`. <br>`/admin/portal/mentors/timeslot/` exposes `list_editable = ('status',)` so the admin can flip a slot to FULL or CANCELLED in bulk. |

### UC-14 &mdash; Post a new signal

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Admin (on behalf of the Mentor)                                                                    |
| Goal             | Publish a new trading signal to the feed.                                                          |
| Main flow        | `/admin/portal/mentors/signal/add/` form collects title, pair, direction, entry, stop-loss, take-profit, mentor. After save, the signal is visible at `/signals/` immediately for subscribers. |

### UC-15 &mdash; Verify payment

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Admin                                                                                              |
| Goal             | Reconcile a payment that looks suspicious or was flagged in the dashboard.                         |
| Main flow        | Open `/admin/portal/bookings/payment/`, filter by status (e.g. PENDING or FAILED), update status manually if needed. |

### UC-16 &mdash; Log out

| Field            | Value                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------|
| Actor            | Customer or Admin                                                                                  |
| Trigger          | Click *Log out* in the navbar.                                                                     |
| Main flow        | POST `/accounts/logout/` clears the session and redirects to the homepage.                         |

---

## 4. Cross-cutting rules

- **Signal access**: `SignalSubscription` is the only plan that unlocks the signal feed; any other plan does not.
- **Booking &harr; Payment invariant**: every booking has exactly one payment (OneToOne); cancelling a booking marks the payment REFUNDED.
- **Slot capacity**: a slot's `capacity` defaults to 1; the booking view refuses to create a booking when `seats_left <= 0`.
- **Future-only bookings**: any attempt to book a slot whose date is before today is rejected with an error.
- **Time zone**: all timestamps and slot times are stored as UTC; templates render in UTC.
