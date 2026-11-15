from django.contrib import admin
from .models import MailJob

@admin.register(MailJob)
class MailJobAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "application",
        "to_email",
        "campaign",
        "status",
        "created_at",
        "sent_at"
    )

    list_filter = ("status", "campaign")

    search_fields = ("to_email",)