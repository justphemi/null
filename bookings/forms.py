"""Forms for bookings: a simple booking form.

Users don't pick plans/products anymore — they just book a session slot and
choose the *type* of session they want (Coaching, Group, or Signal Session).
Mentor / plan detail pages have been removed to keep the UX minimal.
"""
from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    """Collects session type + optional notes for an open time slot."""

    class Meta:
        model = Booking
        fields = ('session_type', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Anything we should know? (optional)',
            }),
        }
