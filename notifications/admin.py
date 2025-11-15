"""Admin registration for notifications models."""
from django.contrib import admin
from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('to', 'sent_at')
    readonly_fields = ('to', 'message', 'sent_at')
