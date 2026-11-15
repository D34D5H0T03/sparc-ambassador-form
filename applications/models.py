from pathlib import Path
from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models

from .validators import validate_bio_word_count, validate_photo_size

# we don't use user supplied filenames
def photo_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"ambassador_photos/{uuid4().hex}{extension}"


class AmbassadorApplications(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
    class StudyYear(models.TextChoices):
        FIRST = "1st", "1st Year"
        SECOND = "2nd", "2nd Year"
        THIRD = "3rd", "3rd Year"
        FOURTH = "4th", "4th Year"
        POSTGRADUATE = "postgraduate", "Postgraduate"

    class IeeeGrade(models.TextChoices):
        STUDENT = "student", "Student Member"
        GRADUATE_STUDENT = "graduate", "Graduate Student Member"
        MEMBER = "member", "Member"
        OTHER = "other", "Other"

    class ReferralSource(models.TextChoices):
        SOCIAL_MEDIA = "social_media", "Social Media"
        FRIEND = "friend", "Friend"
        IEEE_BRANCH = "ieee_branch", "IEEE Student Branch"
        UNIVERSITY = "university", "University"
        WEBSITE = "website", "Website"
        EVENT = "event", "Event"
        OTHER = "other", "Other"
    
    
    # Personal Information
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    whatsapp_number = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=15, choices=Gender.choices)
    
    # University Information
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=150)
    year_of_study = models.CharField(max_length=20, choices=StudyYear.choices)
    student_id = models.CharField(max_length=100)
    
    # IEEE information
    is_ieee_member = models.BooleanField(default=False)
    ieee_membership_number = models.CharField(max_length=100, blank=True)
    ieee_membership_grade = models.CharField(
        max_length=30,
        choices=IeeeGrade.choices,
        blank=True,
    )
    ieee_student_branch = models.CharField(max_length=150, blank=True)
    ieee_position = models.CharField(max_length=150, blank=True) 
    
    # photos and biography
    photo = models.ImageField(
        upload_to=photo_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
            validate_photo_size,
        ],
    )
    bio = models.TextField(validators=[validate_bio_word_count])
    
    # About You
    motivation = models.TextField()
    activities = models.JSONField(default=list)
    referral_source = models.CharField(
        max_length=30,
        choices=ReferralSource.choices,
    )
    
    # Agreements
    confirmed_accuracy = models.BooleanField(default=False)
    agreed_photo_usage = models.BooleanField(default=False)
    understood_point_system = models.BooleanField(default=False)
    agreed_contact = models.BooleanField(default=False)

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Ambassador Application"
        verbose_name_plural = "Ambassador Applications"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.email})"