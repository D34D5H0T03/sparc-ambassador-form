from django.db import transaction
from django.shortcuts import render, redirect
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