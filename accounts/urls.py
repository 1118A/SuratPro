from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/skills/add/', views.add_skill_view, name='add_skill'),
    path('profile/skills/<int:pk>/remove/', views.remove_skill_view, name='remove_skill'),
    path('profile/portfolio/add/', views.add_portfolio_view, name='add_portfolio'),
    path('profile/portfolio/<int:pk>/delete/', views.delete_portfolio_view, name='delete_portfolio'),
    path('profile/<str:username>/', views.profile_view, name='profile_username'),
    path('freelancers/', views.freelancers_list_view, name='freelancers_list'),
]
