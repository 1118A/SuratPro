from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Review
from .forms import ReviewForm
from contracts.models import Contract

@login_required
def leave_review_view(request, contract_pk):
    """Leave a review for a completed contract."""
    contract = get_object_or_404(Contract, pk=contract_pk)
    
    # Validation
    if contract.status != Contract.STATUS_COMPLETED:
        messages.error(request, "You can only leave a review for completed contracts.")
        return redirect('contracts:detail', pk=contract.pk)
        
    if request.user not in [contract.client, contract.freelancer]:
        messages.error(request, "You are not a participant in this contract.")
        return redirect('core:home')
        
    # Determine reviewee
    reviewee = contract.freelancer if request.user == contract.client else contract.client
    
    # Check if already reviewed
    if Review.objects.filter(contract=contract, reviewer=request.user).exists():
        messages.info(request, "You have already left a review for this contract.")
        return redirect('contracts:detail', pk=contract.pk)
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.contract = contract
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()
            
            messages.success(request, f"Review submitted for {reviewee.username}!")
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ReviewForm()
        
    context = {
        'form': form,
        'contract': contract,
        'reviewee': reviewee,
    }
    return render(request, 'reviews/leave_review.html', context)
