from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    
    path('profile/', views.profile_update, name='profile_update'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    path('customers/bulk-upload/', views.customer_bulk_upload, name='customer_bulk_upload'),
    path('customers/download-pdf/', views.customer_download_pdf, name='customer_download_pdf'),
]
