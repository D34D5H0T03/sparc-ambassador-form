from django.db import transaction
from django.shortcuts import render, redirect
from .forms import AmbassadorApplicationsForm

# Email Multi-threading
from threading import Thread
from emails.models import MailJob
from emails.sender import process_job_in_thread

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
                    campaign="ambassador_received",
                    application=application,
                    defaults={
                        "to_email": application.email,
                    },
                )
                transaction.on_commit( # Email sending thread
                    lambda job_id=job.id: Thread(
                        target=process_job_in_thread,
                        args=(job_id,),
                        daemon=True,
                    ).start()
                )
            return redirect("applications:success")
    else:
        form = AmbassadorApplicationsForm()

    return render(
        request,
        "applications/apply.html",
        {"form": form},
    )

def application_success(request):
    return render(
        request,
        "applications/success.html",
    )