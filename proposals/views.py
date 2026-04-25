from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Proposal
from .forms import ProposalForm
from jobs.models import Job
from core.email_utils import email_new_proposal, email_proposal_accepted


@login_required
def submit_proposal_view(request, job_pk):
    """Freelancer submits a proposal on a job."""
    job = get_object_or_404(Job, pk=job_pk, status=Job.STATUS_OPEN)

    if not request.user.is_freelancer:
        messages.error(request, 'Only freelancers can submit proposals.')
        return redirect('jobs:detail', pk=job_pk)
        
    if not request.user.has_paid_registration:
        messages.warning(request, 'You must pay the registration fee before submitting proposals.')
        return redirect('payments:registration_payment')

    if job.client == request.user:
        messages.error(request, 'You cannot bid on your own job.')
        return redirect('jobs:detail', pk=job_pk)

    # Prevent duplicate proposals
    existing = Proposal.objects.filter(job=job, freelancer=request.user).first()
    if existing:
        messages.warning(request, 'You have already submitted a proposal for this job.')
        return redirect('proposals:my_proposals')

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.job = job
            proposal.freelancer = request.user
            proposal.save()
            email_new_proposal(proposal)   # Phase 10: notify client
            messages.success(request, 'Your proposal has been submitted successfully!')
            return redirect('proposals:my_proposals')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ProposalForm()

    return render(request, 'proposals/submit_proposal.html', {
        'form': form,
        'job': job,
    })


@login_required
def my_proposals_view(request):
    """Freelancer: list of all proposals they submitted."""
    if not request.user.is_freelancer:
        return redirect('jobs:list')

    proposals = Proposal.objects.filter(
        freelancer=request.user
    ).select_related('job', 'job__client').order_by('-created_at')

    return render(request, 'proposals/my_proposals.html', {'proposals': proposals})


@login_required
def proposal_detail_view(request, pk):
    """Detail of a single proposal (freelancer or client)."""
    proposal = get_object_or_404(Proposal, pk=pk)

    # Allow only the freelancer who wrote it or the client who owns the job
    if request.user != proposal.freelancer and request.user != proposal.job.client:
        messages.error(request, 'You do not have permission to view this proposal.')
        return redirect('jobs:list')

    return render(request, 'proposals/proposal_detail.html', {'proposal': proposal})


@login_required
def accept_proposal_view(request, pk):
    """Client accepts a proposal → marks job as In Progress."""
    proposal = get_object_or_404(Proposal, pk=pk, job__client=request.user)

    if proposal.job.status != Job.STATUS_OPEN:
        messages.error(request, 'This job is no longer open.')
        return redirect('jobs:detail', pk=proposal.job.pk)

    # Accept this proposal
    proposal.status = Proposal.STATUS_ACCEPTED
    proposal.save(update_fields=['status'])

    # Reject all other pending proposals
    proposal.job.proposals.exclude(pk=proposal.pk).filter(
        status=Proposal.STATUS_PENDING
    ).update(status=Proposal.STATUS_REJECTED)

    # Move job to In Progress
    proposal.job.status = Job.STATUS_INPROG
    proposal.job.save(update_fields=['status'])

    email_proposal_accepted(proposal)   # Phase 10: notify freelancer
    messages.success(
        request,
        f'You have accepted {proposal.freelancer.get_full_name() or proposal.freelancer.username}\'s proposal. The job is now In Progress.'
    )
    return redirect('contracts:detail', pk=proposal.contract.pk)


@login_required
def reject_proposal_view(request, pk):
    """Client rejects a specific proposal."""
    proposal = get_object_or_404(Proposal, pk=pk, job__client=request.user)
    proposal.status = Proposal.STATUS_REJECTED
    proposal.save(update_fields=['status'])
    messages.info(request, 'Proposal rejected.')
    return redirect('jobs:detail', pk=proposal.job.pk)


@login_required
def withdraw_proposal_view(request, pk):
    """Freelancer withdraws their own proposal."""
    proposal = get_object_or_404(Proposal, pk=pk, freelancer=request.user)

    if not proposal.is_pending:
        messages.error(request, 'You can only withdraw pending proposals.')
        return redirect('proposals:my_proposals')

    proposal.status = Proposal.STATUS_WITHDRAWN
    proposal.save(update_fields=['status'])
    messages.info(request, 'Your proposal has been withdrawn.')
    return redirect('proposals:my_proposals')
