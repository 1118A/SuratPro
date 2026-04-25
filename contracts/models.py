from django.db import models
from django.conf import settings
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from proposals.models import Proposal

class Contract(models.Model):
    STATUS_ACTIVE    = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_DISPUTED  = 'disputed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_ACTIVE,    'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DISPUTED,  'Disputed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    job           = models.OneToOneField('jobs.Job', on_delete=models.CASCADE, related_name='contract')
    proposal      = models.OneToOneField('proposals.Proposal', on_delete=models.CASCADE, related_name='contract')
    client        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contracts_as_client')
    freelancer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contracts_as_freelancer')
    agreed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.PositiveIntegerField()
    deadline      = models.DateField(null=True, blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    terms         = models.TextField(blank=True, help_text='Optional terms and milestones agreed upon by the client and freelancer.')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.deadline and self.created_at:
             self.deadline = (self.created_at + timedelta(days=self.delivery_days)).date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contract: {self.job.title} - {self.freelancer.username}"

@receiver(post_save, sender=Proposal)
def create_contract_on_accept(sender, instance, **kwargs):
    """Automatically create a contract when a proposal is accepted."""
    if instance.status == Proposal.STATUS_ACCEPTED:
        # Check if contract already exists
        if not hasattr(instance, 'contract'):
            Contract.objects.create(
                job=instance.job,
                proposal=instance,
                client=instance.job.client,
                freelancer=instance.freelancer,
                agreed_amount=instance.bid_amount,
                delivery_days=instance.delivery_days,
            )
