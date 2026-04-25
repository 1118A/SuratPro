from django import forms
from .models import Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['cover_letter', 'bid_amount', 'delivery_days']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': (
                    'Introduce yourself and explain why you are the right person for this job. '
                    'Mention relevant experience and your approach to the project.'
                ),
            }),
            'bid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your bid in USD',
                'min': '1',
            }),
            'delivery_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 14',
                'min': '1',
            }),
        }
        labels = {
            'cover_letter':   'Cover Letter',
            'bid_amount':     'Your Bid ($)',
            'delivery_days':  'Delivery Time (days)',
        }

    def clean_bid_amount(self):
        amount = self.cleaned_data.get('bid_amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Bid amount must be greater than zero.')
        return amount

    def clean_delivery_days(self):
        days = self.cleaned_data.get('delivery_days')
        if days and days <= 0:
            raise forms.ValidationError('Delivery time must be at least 1 day.')
        return days
