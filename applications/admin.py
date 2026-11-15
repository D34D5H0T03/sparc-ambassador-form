from django.contrib import admin
from .models import AmbassadorApplications


@admin.register(AmbassadorApplications)
class AmbassadorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "university",
        "year_of_study",
        "is_ieee_member",
        "submitted_at",
    )
    list_filter = (
        "is_ieee_member",
        "year_of_study",
        "gender",
        "referral_source",
        "submitted_at",
    )
    search_fields = (
        "full_name",
        "email",
        "whatsapp_number",
        "student_id",
        "university",
        "ieee_membership_number",
    )
    readonly_fields = ("submitted_at",)
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "full_name",
                    "email",
                    "whatsapp_number",
                    "date_of_birth",
                    "gender",
                )
            },
        ),
        (
            "University Information",
            {
                "fields": (
                    "university",
                    "department",
                    "year_of_study",
                    "student_id",
                )
            },
        ),
        (
            "IEEE Membership Details",
            {
                "fields": (
                    "is_ieee_member",
                    "ieee_membership_number",
                    "ieee_membership_grade",
                    "ieee_student_branch",
                    "ieee_position",
                )
            },
        ),
        (
            "Profile & Application Responses",
            {
                "fields": (
                    "photo",
                    "bio",
                    "motivation",
                    "activities",
                    "referral_source",
                )
            },
        ),
        (
            "Agreements & Metadata",
            {
                "fields": (
                    "confirmed_accuracy",
                    "agreed_photo_usage",
                    "understood_point_system",
                    "agreed_contact",
                    "submitted_at",
                )
            },
        ),
    )