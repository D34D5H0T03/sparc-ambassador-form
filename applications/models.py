from pathlib import Path
from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models

from .constants import (
    ALLOWED_PHOTO_EXTENSIONS,
    GENDER_CHOICES,
    IEEE_GRADE_CHOICES,
    MAX_CHOICE_LENGTH,
    MAX_DEPARTMENT_LENGTH,
    MAX_ID_LENGTH,
    MAX_INSTITUTION_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    PHOTO_UPLOAD_SUBDIR,
    REFERRAL_SOURCE_CHOICES,
    STUDY_YEAR_CHOICES,
)
from .validators import validate_bio_word_count, validate_photo_size


def photo_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"{PHOTO_UPLOAD_SUBDIR}/{uuid4().hex}{extension}"


class AmbassadorApplications(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=MAX_NAME_LENGTH)
    email = models.EmailField(unique=True)
    whatsapp_number = models.CharField(max_length=MAX_PHONE_LENGTH)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=MAX_CHOICE_LENGTH, choices=GENDER_CHOICES)

    # University Information
    university = models.CharField(max_length=MAX_INSTITUTION_LENGTH)
    department = models.CharField(max_length=MAX_DEPARTMENT_LENGTH)
    year_of_study = models.CharField(
        max_length=MAX_CHOICE_LENGTH,
        choices=STUDY_YEAR_CHOICES,
    )
    student_id = models.CharField(max_length=MAX_ID_LENGTH)

    # IEEE Information
    is_ieee_member = models.BooleanField(default=False)
    ieee_membership_number = models.CharField(max_length=MAX_ID_LENGTH, blank=True)
    ieee_membership_grade = models.CharField(
        max_length=MAX_CHOICE_LENGTH,
        choices=IEEE_GRADE_CHOICES,
        blank=True,
    )
    ieee_student_branch = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
    ieee_position = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)

    # Photo and Biography
    photo = models.ImageField(
        upload_to=photo_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_PHOTO_EXTENSIONS),
            validate_photo_size,
        ],
    )
    bio = models.TextField(validators=[validate_bio_word_count])

    # About You
    motivation = models.TextField()
    activities = models.JSONField(default=list)
    referral_source = models.CharField(
        max_length=MAX_CHOICE_LENGTH,
        choices=REFERRAL_SOURCE_CHOICES,
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