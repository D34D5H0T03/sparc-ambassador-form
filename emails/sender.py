import base64
from email.message import EmailMessage

from django.conf import settings
from django.core.validators import validate_email
from django.db import close_old_connections
from django.template.loader import render_to_string
from django.utils import timezone
from googleapiclient.discovery import build

from .constants import (
    GMAIL_USER_ID,
    LOCAL_HOSTS,
    MAX_ERROR_LOG_LENGTH,
    OAUTH_INIT_PATH,
    STATIC_LOGO_PATH,
    SUBJECT_APPLICATION_RECEIVED,
    TEMPLATE_RECEIVED_HTML,
    TEMPLATE_RECEIVED_TXT,
)
from .google_auth import get_credentials
from .models import MailJob


def build_service():
    creds = get_credentials()

    if not creds:
        raise RuntimeError(
            f"Google API needs re-authorisation. Visit {OAUTH_INIT_PATH} as a staff user."
        )

    api_name = getattr(settings, "GOOGLE_MAIL_API_NAME", "gmail")
    api_version = getattr(settings, "GOOGLE_MAIL_API_VERSION", "v1")

    return build(
        api_name,
        api_version,
        credentials=creds,
        cache_discovery=False,
    )


def send_mail(service, to, name):
    validate_email(to)

    site_url = getattr(settings, "SITE_URL", "")
    logo_url = ""
    if site_url and not any(host in site_url for host in LOCAL_HOSTS):
        logo_url = f"{site_url}{STATIC_LOGO_PATH}"

    context = {
        "name": name,
        "logo_url": logo_url,
    }

    msg = EmailMessage()
    msg["From"] = settings.MAIL_SENDER
    msg["To"] = to
    msg["Subject"] = SUBJECT_APPLICATION_RECEIVED

    msg.set_content(
        render_to_string(
            TEMPLATE_RECEIVED_TXT,
            context,
        )
    )

    msg.add_alternative(
        render_to_string(
            TEMPLATE_RECEIVED_HTML,
            context,
        ),
        subtype="html",
    )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    result = (
        service.users()
        .messages()
        .send(userId=GMAIL_USER_ID, body={"raw": raw})
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
        print(
            f"[OK] ID={application.id} Name={application.full_name} "
            f"Email={job.to_email} MsgId={job.gmail_message_id}",
            flush=True,
        )

    except Exception as exc:
        job.status = MailJob.Status.FAILED
        job.error = str(exc)[:MAX_ERROR_LOG_LENGTH]
        print(
            f"[FAIL] ID={application.id} Name={application.full_name} "
            f"Reason={job.error}",
            flush=True,
        )

    job.save()
    return job


def process_job_in_thread(job_id):
    close_old_connections()
    try:
        process_job(job_id)
    finally:
        close_old_connections()