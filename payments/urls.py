from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('registration/', views.registration_payment_view, name='registration_payment'),
    path('contract/<int:pk>/checkout/', views.contract_checkout_view, name='contract_checkout'),
    path('history/', views.payment_list_view, name='payment_list'),
    path('earnings/', views.earnings_dashboard_view, name='earnings'),
    path('invoice/<int:pk>/', views.invoice_download_view, name='invoice'),
]
