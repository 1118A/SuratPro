from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('contract/<int:contract_pk>/leave-review/', views.leave_review_view, name='leave_review'),
]
