import base64
from email.message import EmailMessage

from django.conf import settings
from django.core.validators import validate_email
from django.db import close_old_connections
from django.template.loader import render_to_string
from django.utils import timezone
from googleapiclient.discovery import build

from .google_auth import get_credentials
from .models import MailJob

SUBJECT = "SPARC 2026 - Ambassador Application Received"


def build_service():
    creds = get_credentials()

    if not creds:
        raise RuntimeError(
            "Google API needs re-authorisation. Visit /init/oauth2/ as a staff user."
        )

    return build(
        settings.GOOGLE_MAIL_API_NAME,
        settings.GOOGLE_MAIL_API_VERSION,
        credentials=creds,
        cache_discovery=False,
    )


def send_mail(service, to, name):
    validate_email(to)
    
    # logo
    logo_url = ""
    if settings.SITE_URL and "localhost" not in settings.SITE_URL and "127.0.0.1" not in settings.SITE_URL:
        logo_url = f"{settings.SITE_URL}/static/images/SPARC26LogoMin.png" # placeholder for logo

    context = {
        "name": name,
        "logo_url": logo_url,
    }
    
    # Headers
    msg = EmailMessage()
    msg["From"] = settings.MAIL_SENDER
    msg["To"] = to
    msg["Subject"] = SUBJECT

    msg.set_content(
        render_to_string(
            "emails/ambassador_received.txt",
            context,
        )
    )
    msg.add_alternative(
        render_to_string(
            "emails/ambassador_received.html",
            context,
        ),
        subtype="html",
    )
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    result = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )

    return result["id"]


def process_job(job_id, service=None):
    job = MailJob.objects.select_related("application").get(pk=job_id)

    if job.status == MailJob.Status.SENT:
        return job

    application = job.application

    try:
        gmail_service = service or build_service()

        message_id = send_mail(
            gmail_service,
            job.to_email,
            application.full_name,
        )

        job.gmail_message_id = message_id
        job.status = MailJob.Status.SENT
        job.error = ""
        job.sent_at = timezone.now()

    except Exception as exc:
        job.status = MailJob.Status.FAILED
        job.error = str(exc)[:500]

    job.save()
    return job


def process_job_in_thread(job_id):
    close_old_connections()
    try:
        process_job(job_id)
    finally:
        close_old_connections()