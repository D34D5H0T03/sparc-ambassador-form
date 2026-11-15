# Custom CLI commands to sent pending emails

from time import sleep

from django.core.management.base import BaseCommand

from emails.models import MailJob
from emails.sender import build_service, process_job


class Command(BaseCommand):
    help = "Retry pending and failed emails."

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-id",
            type=int,
            default=1,
            help="Minimum application ID to process.",
        )

    def handle(self, *args, **options):
        jobs = list(
            MailJob.objects.filter(
                application_id__gte=options["from_id"],
                status__in=[
                    MailJob.Status.PENDING,
                    MailJob.Status.FAILED,
                ],
            ).order_by("application_id")
        )

        if not jobs:
            self.stdout.write("No pending emails.")
            return

        service = build_service()

        failed = []
        sent = 0

        for job in jobs:
            result = process_job(job.id, service)

            if result.status == MailJob.Status.SENT:
                sent += 1
            else:
                failed.append(job.application_id)

            sleep(3)

        self.stdout.write(f"Done. Sent: {sent} Failed: {failed}")

        if failed:
            self.stdout.write(
                f"Restart with: python manage.py send_pending --from-id {failed[0]}"
            )