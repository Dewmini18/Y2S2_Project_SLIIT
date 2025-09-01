# onlineStore/urls.py

from django.urls import path
from . import views

app_name = 'onlineStore' # Good practice to keep app_name

urlpatterns = [
    path('', views.online_store_homepage, name='homepage'),
    path('products/', views.products, name='products'),
    
    # FIX: Corrected view name from `view_product_detail` to `product_detail`
    # FIX: Changed URL parameter from `<int:id>` to `<int:pk>` to match the view
    path('products/<int:pk>/', views.product_detail, name='product_detail'), 
]