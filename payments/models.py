from django.db import models
from django.conf import settings

class Payment(models.Model):
    PAYMENT_TYPE_REGISTRATION = 'registration'
    PAYMENT_TYPE_PROJECT = 'project'
    PAYMENT_TYPE_REFUND = 'refund'
    
    PAYMENT_TYPE_CHOICES = [
        (PAYMENT_TYPE_REGISTRATION, 'Registration Fee'),
        (PAYMENT_TYPE_PROJECT, 'Project Payment'),
        (PAYMENT_TYPE_REFUND, 'Refund/Bonus'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    contract = models.ForeignKey('contracts.Contract', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount charged or refunded.")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Platform commission fee.")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.user.username} - ₹{self.amount}"
