"""Admin registration for the mentors app."""
from django.contrib import admin

from .models import MentorshipPlan, Mentor, TimeSlot, Signal


class TimeSlotInline(admin.TabularInline):
    """Mentor admin page: edit time slots in-place."""
    model = TimeSlot
    extra = 0
    fields = ('date', 'start_time', 'duration_minutes', 'capacity', 'status')
    show_change_link = True


@admin.register(MentorshipPlan)
class MentorshipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'sessions_included')
    list_filter = ('duration_days',)
    search_fields = ('name', 'description')


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'years_experience')
    list_filter = ('specialization',)
    search_fields = ('name', 'bio')
    inlines = [TimeSlotInline]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'date', 'start_time', 'duration_minutes', 'capacity', 'status')
    list_filter = ('status', 'date', 'mentor')
    search_fields = ('mentor__name',)
    list_editable = ('status',)
    date_hierarchy = 'date'


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ('pair', 'direction', 'title', 'mentor', 'entry_price', 'stop_loss', 'take_profit', 'posted_at')
    list_filter = ('pair', 'direction', 'mentor')
    search_fields = ('title', 'pair', 'mentor__name')
    date_hierarchy = 'posted_at'
