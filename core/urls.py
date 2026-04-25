from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('search/', views.global_search_view, name='search'),
]
