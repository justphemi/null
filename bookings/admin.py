"""Admin registration for bookings."""
from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'time_slot', 'plan', 'status', 'created_at')
    list_filter = ('status', 'plan', 'time_slot__date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'notes')
    list_editable = ('status',)
    date_hierarchy = 'created_at'