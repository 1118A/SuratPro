from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q

from .forms import RegisterForm, LoginForm, UserUpdateForm, FreelancerSkillForm
from .models import User
from .skill_models import FreelancerSkill, Skill, PortfolioItem


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        selected_role = request.POST.get('role', User.ROLE_FREELANCER)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SuratPro, {user.first_name}! Your account has been created.')
            if not user.has_paid_registration:
                return redirect('payments:registration_payment')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        selected_role = request.GET.get('role', User.ROLE_FREELANCER)
        form = RegisterForm(initial={'role': selected_role})

    return render(request, 'accounts/register.html', {
        'form': form,
        'selected_role': selected_role,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            if not user.has_paid_registration:
                return redirect('payments:registration_payment')
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    from reviews.models import Review
    reviews_received = Review.objects.filter(reviewee=profile_user).select_related('reviewer').order_by('-created_at')
    avg_rating = reviews_received.aggregate(avg=Avg('rating'))['avg']

    if profile_user.is_freelancer:
        jobs_stat = profile_user.contracts_as_freelancer.filter(status='completed').count()
    else:
        jobs_stat = profile_user.contracts_as_client.filter(status='completed').count()

    skills = profile_user.freelancer_skills.select_related('skill') if profile_user.is_freelancer else None
    # IDs of skills already added — used in template to exclude them from the picker
    user_skill_ids = set(
        profile_user.freelancer_skills.values_list('skill_id', flat=True)
    ) if profile_user.is_freelancer else set()

    portfolio = profile_user.portfolio_items.prefetch_related('skills_used') if profile_user.is_freelancer else None

    context = {
        'profile_user':    profile_user,
        'is_own_profile':  profile_user == request.user,
        'reviews_received': reviews_received,
        'avg_rating':      avg_rating,
        'review_count':    reviews_received.count(),
        'jobs_stat':       jobs_stat,
        'skills':          skills,
        'user_skill_ids':  user_skill_ids,
        'all_skills':      Skill.objects.all().order_by('name'),
        'portfolio':       portfolio,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def add_skill_view(request):
    """Freelancer adds one or more skills to their profile.

    Accepts two modes (both in the same POST):
    - skill_names: typed free-text skill names (new tag input)
    - skills: list of Skill PKs (legacy / future use)
    """
    if not request.user.is_freelancer:
        return redirect('accounts:profile')

    if request.method == 'POST':
        level = request.POST.get('level', FreelancerSkill.LEVEL_INTERMEDIATE)
        added, skipped = [], []

        # ---- Mode 1: typed names ----
        skill_names = request.POST.getlist('skill_names')
        for raw_name in skill_names:
            name = raw_name.strip()
            if not name:
                continue
            # Get or create the global Skill object
            skill_obj, _ = Skill.objects.get_or_create(
                slug=name.lower().replace(' ', '-').replace('/', '-'),
                defaults={'name': name}
            )
            _, created = FreelancerSkill.objects.get_or_create(
                user=request.user, skill=skill_obj,
                defaults={'level': level}
            )
            (added if created else skipped).append(skill_obj.name)

        # ---- Mode 2: skill PKs (checkbox/legacy) ----
        skill_ids = request.POST.getlist('skills')
        single = request.POST.get('skill')
        if not skill_ids and single:
            skill_ids = [single]
        for sid in skill_ids:
            try:
                skill_obj = Skill.objects.get(pk=sid)
            except Skill.DoesNotExist:
                continue
            _, created = FreelancerSkill.objects.get_or_create(
                user=request.user, skill=skill_obj,
                defaults={'level': level}
            )
            (added if created else skipped).append(skill_obj.name)

        if added:
            messages.success(request, f'Skills added: {", ".join(added)}')
        if skipped:
            messages.info(request, f'Already in your profile: {", ".join(skipped)}')

    return redirect('accounts:profile')


@login_required
def remove_skill_view(request, pk):
    """Freelancer removes one of their skills."""
    fs = get_object_or_404(FreelancerSkill, pk=pk, user=request.user)
    name = fs.skill.name
    fs.delete()
    messages.success(request, f'Skill "{name}" removed.')
    return redirect('accounts:profile')


def freelancers_list_view(request):
    """Browse freelancers with skill, rating, keyword and sort filters."""
    from django.db.models import Avg
    freelancers = User.objects.filter(
        role=User.ROLE_FREELANCER, is_active=True
    ).prefetch_related('freelancer_skills__skill')

    q           = request.GET.get('q', '').strip()
    location    = request.GET.get('location', '').strip()
    skill_slugs = request.GET.getlist('skills')
    min_rating  = request.GET.get('rating', '')
    sort        = request.GET.get('sort', '-created_at')

    if q:
        freelancers = freelancers.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(bio__icontains=q)
        )

    if location:
        freelancers = freelancers.filter(location__icontains=location)

    if skill_slugs:
        for slug in skill_slugs:
            freelancers = freelancers.filter(freelancer_skills__skill__slug=slug)

    # Annotate avg rating for sorting/filtering
    freelancers = freelancers.annotate(avg_rating=Avg('reviews_received__rating'))

    if min_rating:
        try:
            freelancers = freelancers.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass

    sort_map = {
        '-created_at': '-created_at',
        'top_rated':   '-avg_rating',
        'most_jobs':   '-id',
    }
    freelancers = freelancers.order_by(sort_map.get(sort, '-created_at')).distinct()

    total_count = freelancers.count()
    paginator   = Paginator(freelancers, 12)
    page_obj    = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj':    page_obj,
        'query':       q,
        'location':    location,
        'skill_slugs': skill_slugs,
        'min_rating':  min_rating,
        'sort':        sort,
        'total_count': total_count,
        'all_skills':  Skill.objects.all().order_by('name'),
    }
    return render(request, 'accounts/freelancers_list.html', context)


# ─── Portfolio Views (Phase 10) ───────────────────────────────────────────────

@login_required
def add_portfolio_view(request):
    """Freelancer adds a new portfolio item."""
    if not request.user.is_freelancer:
        return redirect('accounts:profile')

    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        url         = request.POST.get('url', '').strip()
        image       = request.FILES.get('image')
        skill_ids   = request.POST.getlist('skills_used')

        if not title or not description:
            messages.error(request, 'Title and description are required.')
            return redirect('accounts:profile')

        item = PortfolioItem.objects.create(
            user=request.user,
            title=title,
            description=description,
            url=url,
            image=image,
        )
        if skill_ids:
            item.skills_used.set(Skill.objects.filter(pk__in=skill_ids))

        messages.success(request, f'Portfolio item "{title}" added!')

    return redirect('accounts:profile')


@login_required
def delete_portfolio_view(request, pk):
    """Freelancer deletes one of their portfolio items."""
    item = get_object_or_404(PortfolioItem, pk=pk, user=request.user)
    title = item.title
    item.delete()
    messages.success(request, f'Portfolio item "{title}" deleted.')
    return redirect('accounts:profile')
