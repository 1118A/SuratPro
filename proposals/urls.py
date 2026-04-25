from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    path('my/',                   views.my_proposals_view,      name='my_proposals'),
    path('submit/<int:job_pk>/',  views.submit_proposal_view,   name='submit'),
    path('<int:pk>/',             views.proposal_detail_view,   name='detail'),
    path('<int:pk>/accept/',      views.accept_proposal_view,   name='accept'),
    path('<int:pk>/reject/',      views.reject_proposal_view,   name='reject'),
    path('<int:pk>/withdraw/',    views.withdraw_proposal_view, name='withdraw'),
]
