from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Job, SavedJob
from .forms import JobPostForm
from accounts.models import Skill


def job_list_view(request):
    """Public job board with search, skill, budget and experience filters."""
    jobs = Job.objects.filter(status=Job.STATUS_OPEN).select_related('client').prefetch_related('skills_required')

    q           = request.GET.get('q', '').strip()
    skill_slugs = request.GET.getlist('skills')   # multi-skill filter
    budget_min  = request.GET.get('bmin', '')
    budget_max  = request.GET.get('bmax', '')
    exp         = request.GET.get('exp', '')
    sort        = request.GET.get('sort', '-created_at')

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(client__username__icontains=q)
        )

    if skill_slugs:
        for slug in skill_slugs:
            jobs = jobs.filter(skills_required__slug=slug)

    if budget_min:
        try:
            jobs = jobs.filter(budget_min__gte=int(budget_min))
        except ValueError:
            pass

    if budget_max:
        try:
            jobs = jobs.filter(budget_max__lte=int(budget_max))
        except ValueError:
            pass

    if exp:
        jobs = jobs.filter(experience_level=exp)

    valid_sorts = {
        '-created_at': '-created_at',
        'budget_low':  'budget_min',
        'budget_high': '-budget_max',
    }
    jobs = jobs.order_by(valid_sorts.get(sort, '-created_at')).distinct()

    total_count = jobs.count()
    paginator   = Paginator(jobs, 12)
    page_obj    = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj':    page_obj,
        'all_skills':  Skill.objects.all().order_by('name'),
        'skill_slugs': skill_slugs,
        'q':           q,
        'budget_min':  budget_min,
        'budget_max':  budget_max,
        'exp':         exp,
        'sort':        sort,
        'total_count': total_count,
        'exp_choices': Job.EXP_CHOICES,
    }
    return render(request, 'jobs/job_list.html', context)



def job_detail_view(request, pk):
    """Job detail page; increments view counter."""
    job = get_object_or_404(Job.objects.select_related('client'), pk=pk)

    # Increment view count (simple, not unique-visitor-safe)
    Job.objects.filter(pk=pk).update(views_count=job.views_count + 1)

    user_proposal = None
    if request.user.is_authenticated and request.user.is_freelancer:
        user_proposal = job.proposals.filter(freelancer=request.user).first()

    context = {
        'job':           job,
        'user_proposal': user_proposal,
        'proposals':     job.proposals.select_related('freelancer') if request.user == job.client else None,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_post_view(request):
    """Clients create a new job posting."""
    if not request.user.is_client:
        messages.error(request, 'Only clients can post jobs.')
        return redirect('jobs:list')

    if not request.user.has_paid_registration:
        messages.warning(request, 'You must pay the registration fee before posting a job.')
        return redirect('payments:registration_payment')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()
            form.save_m2m()
            messages.success(request, 'Your job has been posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobPostForm()

    return render(request, 'jobs/job_post.html', {'form': form})


@login_required
def job_edit_view(request, pk):
    """Client edits their own job."""
    job = get_object_or_404(Job, pk=pk, client=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobPostForm(instance=job)

    return render(request, 'jobs/job_post.html', {'form': form, 'editing': True, 'job': job})


@login_required
def job_close_view(request, pk):
    """Client closes a job."""
    job = get_object_or_404(Job, pk=pk, client=request.user)
    job.status = Job.STATUS_CLOSED
    job.save(update_fields=['status'])
    messages.success(request, 'Job closed.')
    return redirect('jobs:detail', pk=job.pk)


@login_required
def my_jobs_view(request):
    """Client dashboard: all jobs posted by this user."""
    if not request.user.is_client:
        return redirect('jobs:list')
    jobs = Job.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})


# ─── Saved Jobs (Phase 10) ──────────────────────────────────────────────

@login_required
def save_job_toggle_view(request, pk):
    """Toggle save/unsave a job for a freelancer."""
    if not request.user.is_freelancer:
        messages.warning(request, 'Only freelancers can save jobs.')
        return redirect('jobs:detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)
    saved, created = SavedJob.objects.get_or_create(freelancer=request.user, job=job)
    if not created:
        saved.delete()
        messages.info(request, f'"{job.title}" removed from saved jobs.')
    else:
        messages.success(request, f'"{job.title}" saved! Find it in Saved Jobs.')
    return redirect('jobs:detail', pk=pk)


@login_required
def saved_jobs_view(request):
    """List of all jobs saved by the current freelancer."""
    if not request.user.is_freelancer:
        return redirect('jobs:list')
    saved = SavedJob.objects.filter(
        freelancer=request.user
    ).select_related('job__client').prefetch_related('job__skills_required')
    return render(request, 'jobs/saved_jobs.html', {'saved': saved})
