from django.contrib.auth.models import AbstractUser
from django.db import models

# Import skill/portfolio models so Django registers them under the accounts app
from .skill_models import Skill, FreelancerSkill, PortfolioItem  # noqa: F401



class User(AbstractUser):
    ROLE_FREELANCER = 'freelancer'
    ROLE_CLIENT = 'client'

    ROLE_CHOICES = [
        (ROLE_FREELANCER, 'Freelancer'),
        (ROLE_CLIENT, 'Client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FREELANCER)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, help_text='Upload your CV/Resume (PDF)')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Registration & Payment logic
    has_paid_registration = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    first_project_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_freelancer(self):
        return self.role == self.ROLE_FREELANCER

    @property
    def is_client(self):
        return self.role == self.ROLE_CLIENT

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default_avatar.png'
