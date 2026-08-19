"""Admin registration for bookings."""
from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'time_slot', 'session_type', 'status', 'created_at')
    list_filter = ('status', 'session_type', 'time_slot__date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'notes')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
