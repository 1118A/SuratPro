from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from accounts.models import User


# Surat-specific service categories
DEFAULT_CATEGORIES = [
    {'name': 'Textile Design',     'icon': 'bi-scissors',        'bg': '#fce7f3', 'color': '#db2777', 'desc': 'Fabric, print & weave design'},
    {'name': 'Web Development',    'icon': 'bi-code-slash',       'bg': '#dbeafe', 'color': '#2563eb', 'desc': 'React, Django, WordPress'},
    {'name': 'Diamond Grading',    'icon': 'bi-gem',              'bg': '#e0f2fe', 'color': '#0284c7', 'desc': 'GIA reports, ERP software'},
    {'name': 'UI/UX Design',       'icon': 'bi-vector-pen',       'bg': '#ede9fe', 'color': '#7c3aed', 'desc': 'Figma, Adobe XD, Branding'},
    {'name': 'Accounting / GST',   'icon': 'bi-calculator',       'bg': '#d1fae5', 'color': '#059669', 'desc': 'GST filing, Tally, bookkeeping'},
    {'name': 'Digital Marketing',  'icon': 'bi-megaphone',        'bg': '#fef3c7', 'color': '#d97706', 'desc': 'SEO, Meta Ads, WhatsApp'},
    {'name': 'Video & Reels',      'icon': 'bi-camera-video',     'bg': '#fee2e2', 'color': '#dc2626', 'desc': 'Product reels, YouTube, ads'},
    {'name': 'Mobile Apps',        'icon': 'bi-phone',            'bg': '#fef9c3', 'color': '#ca8a04', 'desc': 'Android & iOS development'},
]


def home_view(request):
    top_freelancers = User.objects.filter(
        role=User.ROLE_FREELANCER,
        is_active=True
    ).order_by('-created_at')[:6]

    context = {
        'top_freelancers':    top_freelancers,
        'default_categories': DEFAULT_CATEGORIES,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')


@staff_member_required(login_url='accounts:login')
def admin_dashboard_view(request):
    """Staff-only analytics dashboard."""
    from jobs.models import Job
    from contracts.models import Contract
    from payments.models import Payment

    total_users       = User.objects.count()
    total_freelancers = User.objects.filter(role=User.ROLE_FREELANCER).count()
    total_clients     = User.objects.filter(role=User.ROLE_CLIENT).count()

    total_jobs_open   = Job.objects.filter(status=Job.STATUS_OPEN).count()
    total_jobs_closed = Job.objects.filter(status=Job.STATUS_CLOSED).count()
    total_jobs_inprog = Job.objects.filter(status=Job.STATUS_INPROG).count()
    total_jobs        = total_jobs_open + total_jobs_closed + total_jobs_inprog

    total_contracts_active    = Contract.objects.filter(status=Contract.STATUS_ACTIVE).count()
    total_contracts_completed = Contract.objects.filter(status=Contract.STATUS_COMPLETED).count()
    total_contracts           = Contract.objects.count()

    total_revenue = Payment.objects.filter(
        payment_type=Payment.PAYMENT_TYPE_PROJECT,
        status=Payment.STATUS_COMPLETED
    ).aggregate(total=Sum('fee'))['total'] or 0

    total_collected = Payment.objects.filter(
        status=Payment.STATUS_COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or 0

    recent_payments = Payment.objects.select_related('user', 'contract').order_by('-created_at')[:10]
    recent_signups  = User.objects.order_by('-date_joined')[:10]

    context = {
        'total_users': total_users,
        'total_freelancers': total_freelancers,
        'total_clients': total_clients,
        'total_jobs': total_jobs,
        'total_jobs_open': total_jobs_open,
        'total_jobs_closed': total_jobs_closed,
        'total_jobs_inprog': total_jobs_inprog,
        'total_contracts': total_contracts,
        'total_contracts_active': total_contracts_active,
        'total_contracts_completed': total_contracts_completed,
        'total_revenue': total_revenue,
        'total_collected': total_collected,
        'recent_payments': recent_payments,
        'recent_signups': recent_signups,
    }
    return render(request, 'core/admin_dashboard.html', context)


def global_search_view(request):
    """Phase 7: Single search endpoint — searches jobs AND freelancers."""
    from django.db.models import Q, Avg
    from jobs.models import Job
    q = request.GET.get('q', '').strip()

    jobs = []
    freelancers = []

    if q:
        jobs = Job.objects.filter(
            status=Job.STATUS_OPEN
        ).filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        ).select_related('client').prefetch_related('skills_required')[:8]

        freelancers = User.objects.filter(
            role=User.ROLE_FREELANCER, is_active=True
        ).filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(bio__icontains=q)
        ).annotate(avg_rating=Avg('reviews_received__rating'))[:8]

    context = {
        'q':           q,
        'jobs':        jobs,
        'freelancers': freelancers,
        'job_count':   len(jobs),
        'fl_count':    len(freelancers),
    }
    return render(request, 'core/search_results.html', context)

