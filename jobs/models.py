from django.db import models
from django.conf import settings
from django.utils import timezone


class Job(models.Model):
    """A job posted by a Client."""

    # Status
    STATUS_OPEN   = 'open'
    STATUS_INPROG = 'in_progress'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN,   'Open'),
        (STATUS_INPROG, 'In Progress'),
        (STATUS_CLOSED, 'Closed'),
    ]

    # Budget type
    BUDGET_FIXED  = 'fixed'
    BUDGET_HOURLY = 'hourly'

    BUDGET_CHOICES = [
        (BUDGET_FIXED,  'Fixed Price'),
        (BUDGET_HOURLY, 'Hourly Rate'),
    ]

    # Experience level
    EXP_ENTRY       = 'entry'
    EXP_INTERMEDIATE = 'intermediate'
    EXP_EXPERT      = 'expert'

    EXP_CHOICES = [
        (EXP_ENTRY,        'Entry Level'),
        (EXP_INTERMEDIATE, 'Intermediate'),
        (EXP_EXPERT,       'Expert'),
    ]

    client       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_posted',
    )
    title        = models.CharField(max_length=255)
    description  = models.TextField()
    skills_required = models.ManyToManyField(
        'accounts.Skill',
        blank=True,
        related_name='jobs',
    )
    budget_type  = models.CharField(max_length=10, choices=BUDGET_CHOICES, default=BUDGET_FIXED)
    budget_min   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_max   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline     = models.DateField(null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXP_CHOICES, default=EXP_INTERMEDIATE)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    views_count  = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} (by {self.client.username})'

    @property
    def budget_display(self):
        if self.budget_type == self.BUDGET_HOURLY:
            return f'₹{self.budget_min}–₹{self.budget_max}/hr'
        return f'₹{self.budget_min}–₹{self.budget_max}'

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    @property
    def proposal_count(self):
        return self.proposals.count()


class SavedJob(models.Model):
    """A freelancer bookmarks / saves a job to apply later."""
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('freelancer', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f'{self.freelancer.username} saved "{self.job.title}"'
