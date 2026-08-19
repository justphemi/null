"""Forms for bookings: a simple booking form.

Users pick a plan (price tier) for the slot they're booking. The slot
itself comes from the admin-set availability on the previous page.
"""
from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    """Collects plan + optional notes for an open time slot."""

    class Meta:
        model = Booking
        fields = ('plan', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Anything we should know? (optional)',
            }),
        }
