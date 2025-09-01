from django.urls import path
from . import views

app_name = 'non_medicine'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('table/', views.product_table, name='product_table'),
    path('create/', views.product_create, name='product_create'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/update/', views.product_update, name='product_update'),
    path('<slug:slug>/delete/', views.product_delete, name='product_delete'),

    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),
]