from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.my_contracts_view, name='my_contracts'),
    path('<int:pk>/', views.contract_detail_view, name='detail'),
    path('<int:pk>/complete/', views.mark_complete_view, name='mark_complete'),
]
