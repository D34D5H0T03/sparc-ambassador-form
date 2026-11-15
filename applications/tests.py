import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from emails.models import MailJob

from .constants import (
    CAMPAIGN_APPLICATION_RECEIVED,
    MAX_BIO_WORD_COUNT,
    MAX_PHOTO_SIZE_BYTES,
)
from .forms import AmbassadorApplicationsForm
from .models import AmbassadorApplications

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def make_test_image(name="photo.png", size=(100, 100), fmt="PNG"):
    buffer = BytesIO()
    Image.new("RGB", size, color=(0, 98, 155)).save(buffer, format=fmt)
    buffer.seek(0)
    content_type = "image/png" if fmt == "PNG" else "image/jpeg"
    return SimpleUploadedFile(name, buffer.read(), content_type=content_type)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AmbassadorApplicationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def _base_form_data(self):
        return {
            "full_name": "Nadia Rahman",
            "email": "Nadia.Rahman@Example.com",
            "whatsapp_number": "+8801711000000",
            "date_of_birth": "2004-05-14",
            "gender": "female",
            "university": "North South University",
            "department": "Electrical and Computer Engineering",
            "year_of_study": "3rd",
            "student_id": "2211234042",
            "is_ieee_member": False,
            "bio": "Nadia is a third-year Computer Science student passionate about campus tech outreach.",
            "motivation": "I want to organize workshops and connect students with SPARC.",
            "activities": ["social_media_posts", "campus_sessions"],
            "referral_source": "ieee_branch",
            "confirmed_accuracy": True,
            "agreed_photo_usage": True,
            "understood_point_system": True,
            "agreed_contact": True,
        }

    def test_valid_non_member_form_normalizes_email(self):
        form = AmbassadorApplicationsForm(
            data=self._base_form_data(),
            files={"photo": make_test_image()},
        )
        self.assertTrue(form.is_valid(), form.errors)
        application = form.save()
        self.assertEqual(application.email, "nadia.rahman@example.com")

    def test_ieee_member_requires_membership_details(self):
        data = self._base_form_data()
        data["is_ieee_member"] = True
        form = AmbassadorApplicationsForm(
            data=data,
            files={"photo": make_test_image()},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("ieee_membership_number", form.errors)
        self.assertIn("ieee_membership_grade", form.errors)
        self.assertIn("ieee_student_branch", form.errors)
        self.assertNotIn("ieee_position", form.errors)

    def test_bio_exceeding_max_words_is_rejected(self):
        data = self._base_form_data()
        data["bio"] = " ".join(["word"] * (MAX_BIO_WORD_COUNT + 1))
        form = AmbassadorApplicationsForm(
            data=data,
            files={"photo": make_test_image()},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("bio", form.errors)

    def test_oversized_photo_is_rejected(self):
        oversized_file = SimpleUploadedFile(
            "huge.jpg",
            b"x" * (MAX_PHOTO_SIZE_BYTES + 1),
            content_type="image/jpeg",
        )
        form = AmbassadorApplicationsForm(
            data=self._base_form_data(),
            files={"photo": oversized_file},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("photo", form.errors)

    @patch("applications.views.process_job_in_thread")
    def test_apply_view_saves_application_and_creates_pending_mailjob(self, mock_worker):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("applications:apply"),
                data={**self._base_form_data(), "photo": make_test_image()},
            )

        self.assertRedirects(response, reverse("applications:success"))
        self.assertEqual(AmbassadorApplications.objects.count(), 1)
        job = MailJob.objects.get()
        self.assertEqual(job.campaign, CAMPAIGN_APPLICATION_RECEIVED)
        self.assertEqual(job.status, MailJob.Status.PENDING)
        self.assertEqual(job.to_email, "nadia.rahman@example.com")
        mock_worker.assert_called_once_with(job.id)