from django import forms
from .models import Contract

class ContractTermsForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['terms']
        widgets = {
            'terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Add any specific milestones or terms of agreement here...',
            })
        }
