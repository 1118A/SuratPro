from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Global skill tags that freelancers can attach to their profiles."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FreelancerSkill(models.Model):
    """Many-to-many junction: a freelancer's self-reported proficiency in a skill."""
    LEVEL_BEGINNER     = 'beginner'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_EXPERT       = 'expert'

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER,     'Beginner'),
        (LEVEL_INTERMEDIATE, 'Intermediate'),
        (LEVEL_EXPERT,       'Expert'),
    ]

    user  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='freelancer_skills',
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='freelancer_skills')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INTERMEDIATE)

    class Meta:
        unique_together = ('user', 'skill')
        ordering = ['skill__name']

    def __str__(self):
        return f'{self.user.username} — {self.skill.name} ({self.level})'


class PortfolioItem(models.Model):
    """A portfolio project added by a freelancer."""
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title       = models.CharField(max_length=200)
    description = models.TextField()
    url         = models.URLField(blank=True, help_text='Live project URL (optional)')
    image       = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    skills_used = models.ManyToManyField(Skill, blank=True, related_name='portfolio_items')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.title}'
