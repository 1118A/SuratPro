from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('start/<str:username>/', views.start_conversation_view, name='start_conversation'),
    path('<int:pk>/', views.conversation_view, name='conversation'),
    path('api/unread/', views.unread_count_api, name='unread_count'),
]
