import shutil
import tempfile
from datetime import date
from io import StringIO, BytesIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, override_settings
from PIL import Image

from applications.models import AmbassadorApplications

from .constants import CAMPAIGN_AMBASSADOR_RECEIVED
from .models import MailJob
from .sender import process_job

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def create_sample_application(email="applicant@example.com"):
    buffer = BytesIO()
    Image.new("RGB", (60, 60), color=(0, 98, 155)).save(buffer, format="PNG")
    buffer.seek(0)
    photo = SimpleUploadedFile("avatar.png", buffer.read(), content_type="image/png")

    return AmbassadorApplications.objects.create(
        full_name="Tariq Hasan",
        email=email,
        whatsapp_number="+8801700000000",
        date_of_birth=date(2003, 8, 20),
        gender="male",
        university="North South University",
        department="CSE",
        year_of_study="3rd",
        student_id="2219999042",
        is_ieee_member=False,
        photo=photo,
        bio="Tariq is an engineering undergraduate focused on systems and community events.",
        motivation="Excited to represent SPARC on campus.",
        activities=["campus_sessions"],
        referral_source="university",
        confirmed_accuracy=True,
        agreed_photo_usage=True,
        understood_point_system=True,
        agreed_contact=True,
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class MailJobPipelineTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_unique_mailjob_per_campaign_and_application(self):
        app = create_sample_application()
        MailJob.objects.create(
            campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
            application=app,
            to_email=app.email,
        )
        with self.assertRaises(IntegrityError):
            MailJob.objects.create(
                campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
                application=app,
                to_email=app.email,
            )

    @patch("emails.sender.send_mail", return_value="gmail-msg-12345")
    def test_process_job_marks_sent_and_skips_already_sent(self, mock_send):
        app = create_sample_application()
        job = MailJob.objects.create(
            campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
            application=app,
            to_email=app.email,
        )
        mock_service = MagicMock()

        updated = process_job(job.id, service=mock_service)
        self.assertEqual(updated.status, MailJob.Status.SENT)
        self.assertEqual(updated.gmail_message_id, "gmail-msg-12345")
        self.assertIsNotNone(updated.sent_at)
        mock_send.assert_called_once()

        # Calling process_job again must not dispatch a second email
        process_job(job.id, service=mock_service)
        mock_send.assert_called_once()

    @patch("emails.sender.send_mail", side_effect=RuntimeError("Simulated OAuth failure"))
    def test_process_job_records_failure_without_losing_application(self, _mock_send):
        app = create_sample_application()
        job = MailJob.objects.create(
            campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
            application=app,
            to_email=app.email,
        )

        updated = process_job(job.id, service=MagicMock())
        self.assertEqual(updated.status, MailJob.Status.FAILED)
        self.assertIn("Simulated OAuth failure", updated.error)
        self.assertTrue(AmbassadorApplications.objects.filter(pk=app.pk).exists())

    @patch("emails.management.commands.send_pending.sleep")
    @patch("emails.management.commands.send_pending.build_service", return_value=MagicMock())
    @patch("emails.sender.send_mail", return_value="gmail-retry-999")
    def test_send_pending_command_retries_failed_and_skips_sent(
        self, mock_send, _mock_build, _mock_sleep
    ):
        app1 = create_sample_application("sent@example.com")
        app2 = create_sample_application("failed@example.com")

        MailJob.objects.create(
            campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
            application=app1,
            to_email=app1.email,
            status=MailJob.Status.SENT,
            gmail_message_id="already-sent-id",
        )
        failed_job = MailJob.objects.create(
            campaign=CAMPAIGN_AMBASSADOR_RECEIVED,
            application=app2,
            to_email=app2.email,
            status=MailJob.Status.FAILED,
            error="Temporary error",
        )

        stdout = StringIO()
        call_command("send_pending", stdout=stdout)

        failed_job.refresh_from_db()
        self.assertEqual(failed_job.status, MailJob.Status.SENT)
        self.assertEqual(failed_job.gmail_message_id, "gmail-retry-999")
        mock_send.assert_called_once()
        self.assertIn("Done. Sent: 1 Failed: []", stdout.getvalue())