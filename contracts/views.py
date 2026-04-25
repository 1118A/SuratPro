from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Contract
from .forms import ContractTermsForm
from jobs.models import Job

@login_required
def contract_detail_view(request, pk):
    """View a specific contract."""
    contract = get_object_or_404(Contract, pk=pk)

    # Ensure only the client or freelancer involved can view
    if request.user != contract.client and request.user != contract.freelancer:
        messages.error(request, 'You do not have permission to view this contract.')
        return redirect('core:home')

    form = None
    if request.user == contract.client and contract.status == Contract.STATUS_ACTIVE:
        if request.method == 'POST':
            form = ContractTermsForm(request.POST, instance=contract)
            if form.is_valid():
                form.save()
                messages.success(request, 'Contract terms updated successfully.')
                return redirect('contracts:detail', pk=contract.pk)
        else:
            form = ContractTermsForm(instance=contract)

    context = {
        'contract': contract,
        'form': form,
    }
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def my_contracts_view(request):
    """List of all contracts for the current user."""
    contracts = Contract.objects.filter(
        Q(client=request.user) | Q(freelancer=request.user)
    ).select_related('job', 'client', 'freelancer').order_by('-created_at')

    return render(request, 'contracts/my_contracts.html', {'contracts': contracts})


@login_required
def mark_complete_view(request, pk):
    """Client marks a contract as completed."""
    contract = get_object_or_404(Contract, pk=pk, client=request.user)
    
    if contract.status != Contract.STATUS_ACTIVE:
        messages.error(request, 'Only active contracts can be marked as complete.')
        return redirect('contracts:detail', pk=contract.pk)

    if request.method == 'POST':
        from django.db import transaction
        from payments.models import Payment
        
        with transaction.atomic():
            # Complete the contract
            contract.status = Contract.STATUS_COMPLETED
            contract.save(update_fields=['status'])

            # Complete the job as well
            job = contract.job
            job.status = Job.STATUS_CLOSED
            job.save(update_fields=['status'])
            
            # ---------------------------------------------------------
            # Payout Logic
            # ---------------------------------------------------------
            freelancer = contract.freelancer
            contract_amount = contract.agreed_amount
            
            # Pay freelancer (Add to wallet balance)
            freelancer.wallet_balance += contract_amount
            
            # Check for first project refund
            if not freelancer.first_project_completed:
                freelancer.first_project_completed = True
                freelancer.wallet_balance += 100  # Refund the registration fee
                
                # Log the refund payment
                Payment.objects.create(
                    user=freelancer,
                    contract=contract,
                    payment_type=Payment.PAYMENT_TYPE_REFUND,
                    amount=100.00,
                    status=Payment.STATUS_COMPLETED
                )
                messages.success(request, 'Freelancer was also refunded their registration fee.')
                
            freelancer.save(update_fields=['wallet_balance', 'first_project_completed'])

        messages.success(request, 'Contract marked as complete! Funds have been released to the freelancer.')
        return redirect('contracts:detail', pk=contract.pk)

    return redirect('contracts:detail', pk=contract.pk)
