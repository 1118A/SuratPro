from django import forms
from .models import Job
from accounts.models import Skill


class JobPostForm(forms.ModelForm):
    """
    Job posting form.

    Key fix: skills_required is a ManyToManyField with blank=True on the model,
    but Django's ModelForm still generates a required=True ModelMultipleChoiceField
    unless we override it explicitly. We do that below.
    """

    # Explicit field override: optional, uses checkboxes
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Required Skills (optional)',
        help_text='Select all skills that are needed for this project.',
    )

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'budget_type',
            'budget_min', 'budget_max', 'deadline',
            'experience_level', 'skills_required',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Build a React dashboard for SaaS app',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Describe the project scope, deliverables, and any technical requirements...',
            }),
            'budget_type': forms.Select(attrs={'class': 'form-select'}),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '500',
                'min': '0',
                'step': '0.01',
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2000',
                'min': '0',
                'step': '0.01',
            }),
            'deadline': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'budget_min': 'Min Budget ($)',
            'budget_max': 'Max Budget ($)',
        }

    def clean(self):
        cleaned = super().clean()
        min_b = cleaned.get('budget_min') or 0
        max_b = cleaned.get('budget_max') or 0
        if max_b > 0 and min_b > 0 and max_b < min_b:
            self.add_error('budget_max', 'Maximum budget must be greater than or equal to minimum budget.')
        return cleaned
