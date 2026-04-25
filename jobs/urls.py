from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('',                       views.job_list_view,       name='list'),
    path('post/',                  views.job_post_view,       name='post'),
    path('my-jobs/',               views.my_jobs_view,        name='my_jobs'),
    path('saved/',                 views.saved_jobs_view,     name='saved_jobs'),
    path('<int:pk>/',              views.job_detail_view,     name='detail'),
    path('<int:pk>/edit/',         views.job_edit_view,       name='edit'),
    path('<int:pk>/close/',        views.job_close_view,      name='close'),
    path('<int:pk>/save/',         views.save_job_toggle_view, name='save_toggle'),
]
