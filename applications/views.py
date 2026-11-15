from threading import Thread

from django.db import transaction
from django.shortcuts import redirect, render

from emails.models import MailJob
from emails.sender import process_job_in_thread

from .constants import (
    BIO_WARNING_WORD_THRESHOLD,
    CAMPAIGN_APPLICATION_RECEIVED,
    MAX_BIO_WORD_COUNT,
    MAX_PHOTO_SIZE_BYTES,
    MAX_PHOTO_SIZE_MB,
)
from .forms import AmbassadorApplicationsForm


def welcome(request):
    return render(
        request,
        "applications/welcome.html",
    )


def apply(request):
    if request.method == "POST":
        form = AmbassadorApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                application = form.save()
                job, _ = MailJob.objects.get_or_create(
                    campaign=CAMPAIGN_APPLICATION_RECEIVED,
                    application=application,
                    defaults={
                        "to_email": application.email,
                    },
                )
                transaction.on_commit(
                    lambda job_id=job.id: Thread(
                        target=process_job_in_thread,
                        args=(job_id,),
                        daemon=True,
                    ).start()
                )
            return redirect("applications:success")
    else:
        form = AmbassadorApplicationsForm()

    context = {
        "form": form,
        "max_bio_words": MAX_BIO_WORD_COUNT,
        "bio_warning_words": BIO_WARNING_WORD_THRESHOLD,
        "max_photo_bytes": MAX_PHOTO_SIZE_BYTES,
        "max_photo_mb": MAX_PHOTO_SIZE_MB,
    }
    return render(
        request,
        "applications/apply.html",
        context,
    )


def application_success(request):
    return render(
        request,
        "applications/success.html",
    )