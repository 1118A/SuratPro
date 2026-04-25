from django.db import models
from django.conf import settings


class Proposal(models.Model):
    """A bid submitted by a Freelancer on a Job."""

    STATUS_PENDING  = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_ACCEPTED,  'Accepted'),
        (STATUS_REJECTED,  'Rejected'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    job        = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='proposals',
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proposals_submitted',
    )
    cover_letter    = models.TextField(help_text='Explain why you are the best fit.')
    bid_amount      = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days   = models.PositiveIntegerField(help_text='Estimated days to complete.')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    client_note     = models.TextField(blank=True, help_text='Internal note from the client (not shown to freelancer).')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('job', 'freelancer')  # one proposal per freelancer per job

    def __str__(self):
        return f'Proposal by {self.freelancer.username} on "{self.job.title}"'

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_accepted(self):
        return self.status == self.STATUS_ACCEPTED
