from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('processing/<int:order_id>/', views.order_processing, name='order_processing'),
    path('status/<int:order_id>/', views.check_payment_status, name='check_payment_status'),
]
