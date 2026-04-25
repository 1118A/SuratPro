from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Payment
from contracts.models import Contract

@login_required
def registration_payment_view(request):
    """View where user pays their initial registration fee."""
    if request.user.has_paid_registration:
        messages.info(request, "You have already paid the registration fee.")
        return redirect('core:home')
        
    fee = 100.00 if request.user.is_freelancer else 200.00
    
    if request.method == 'POST':
        with transaction.atomic():
            # Create payment record
            Payment.objects.create(
                user=request.user,
                payment_type=Payment.PAYMENT_TYPE_REGISTRATION,
                amount=fee,
                status=Payment.STATUS_COMPLETED
            )
            
            # Update user
            request.user.has_paid_registration = True
            if request.user.is_client:
                request.user.wallet_balance += fee
            request.user.save()
            
        messages.success(request, "Registration payment successful! Welcome to SuratPro.")
        return redirect('core:home')
        
    context = {
        'fee': fee,
    }
    return render(request, 'payments/registration_payment.html', context)


@login_required
def contract_checkout_view(request, pk):
    """Checkout page for a specific contract."""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.user != contract.client:
        messages.error(request, "Only the client can pay for this contract.")
        return redirect('contracts:detail', pk=contract.pk)
        
    # Check if already paid
    if contract.payments.filter(payment_type=Payment.PAYMENT_TYPE_PROJECT, status=Payment.STATUS_COMPLETED).exists():
        messages.info(request, "This contract has already been paid for.")
        return redirect('contracts:detail', pk=contract.pk)
        
    # Calculation
    contract_amount = float(contract.agreed_amount)
    platform_fee = contract_amount * 0.20  # 20% commission
    total_due = contract_amount + platform_fee
    
    wallet_balance = float(request.user.wallet_balance)
    amount_to_pay = max(0, total_due - wallet_balance)
    wallet_used = min(wallet_balance, total_due)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Create payment
            Payment.objects.create(
                user=request.user,
                contract=contract,
                payment_type=Payment.PAYMENT_TYPE_PROJECT,
                amount=amount_to_pay,
                fee=platform_fee,
                status=Payment.STATUS_COMPLETED
            )
            
            # Deduct wallet
            if wallet_used > 0:
                request.user.wallet_balance -= wallet_used
                request.user.save()
            
        messages.success(request, f"Payment successful. Project is now funded in escrow.")
        return redirect('contracts:detail', pk=contract.pk)
        
    context = {
        'contract': contract,
        'contract_amount': contract_amount,
        'platform_fee': platform_fee,
        'total_due': total_due,
        'wallet_balance': wallet_balance,
        'wallet_used': wallet_used,
        'amount_to_pay': amount_to_pay,
    }
    return render(request, 'payments/contract_checkout.html', context)

@login_required
def payment_list_view(request):
    """List of all payments for the user."""
    payments = request.user.payments.all()
    return render(request, 'payments/payment_list.html', {'payments': payments})


@login_required
def earnings_dashboard_view(request):
    """Phase 9: Freelancer earnings dashboard with monthly breakdown."""
    if not request.user.is_freelancer:
        messages.error(request, 'This page is for freelancers only.')
        return redirect('core:home')

    from django.db.models import Sum, Count
    from django.db.models.functions import TruncMonth
    from datetime import date, timedelta
    from contracts.models import Contract

    # All completed project payments on contracts where user is freelancer
    earned_payments = Payment.objects.filter(
        contract__freelancer=request.user,
        payment_type=Payment.PAYMENT_TYPE_PROJECT,
        status=Payment.STATUS_COMPLETED,
    )

    total_earned    = earned_payments.aggregate(t=Sum('amount'))['t'] or 0
    total_fees_paid = earned_payments.aggregate(t=Sum('fee'))['t'] or 0
    net_earned      = float(total_earned) - float(total_fees_paid)

    # Pending: active contracts not yet paid
    pending_contracts = Contract.objects.filter(
        freelancer=request.user,
        status=Contract.STATUS_ACTIVE
    ).exclude(payments__status=Payment.STATUS_COMPLETED)
    pending_value = pending_contracts.aggregate(t=Sum('agreed_amount'))['t'] or 0

    # Monthly data for last 6 months
    six_months_ago = date.today().replace(day=1)
    for _ in range(5):
        six_months_ago = (six_months_ago - timedelta(days=1)).replace(day=1)

    monthly_raw = (
        earned_payments
        .filter(created_at__date__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    monthly_data = [
        {'label': m['month'].strftime('%b %Y'), 'total': float(m['total'])}
        for m in monthly_raw
    ]
    max_monthly = max((m['total'] for m in monthly_data), default=1)

    context = {
        'total_earned':       total_earned,
        'total_fees_paid':    total_fees_paid,
        'net_earned':         net_earned,
        'pending_value':      pending_value,
        'earned_payments':    earned_payments.select_related('contract__job').order_by('-created_at')[:20],
        'monthly_data':       monthly_data,
        'max_monthly':        max_monthly,
        'pending_contracts':  pending_contracts.select_related('job')[:5],
    }
    return render(request, 'payments/earnings.html', context)


@login_required
def invoice_download_view(request, pk):
    """Phase 9: Render a print-ready invoice for a completed contract."""
    contract = get_object_or_404(Contract, pk=pk)

    # Only client or freelancer may view
    if request.user not in (contract.client, contract.freelancer):
        messages.error(request, 'Access denied.')
        return redirect('contracts:list')

    payment = contract.payments.filter(
        payment_type=Payment.PAYMENT_TYPE_PROJECT,
        status=Payment.STATUS_COMPLETED
    ).first()

    context = {
        'contract': contract,
        'payment':  payment,
    }
    return render(request, 'payments/invoice.html', context)

