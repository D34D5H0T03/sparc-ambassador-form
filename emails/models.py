from django.db import models

class MailJob(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    campaign = models.CharField(max_length=40)
    
    # relation with application
    application = models.ForeignKey(
        "applications.AmbassadorApplications",
        on_delete=models.CASCADE,
        related_name="mail_jobs"
    )

    to_email = models.EmailField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    error = models.TextField(blank=True)

    gmail_message_id = models.CharField(
        max_length=64,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "application"],
                name="one_mail_per_campaign"
            )
        ]

    def __str__(self):
        return f"{self.campaign} - {self.to_email} ({self.status})"