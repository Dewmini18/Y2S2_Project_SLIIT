from django.urls import path
from Pharmarcy_Prescription_Tracker import settings
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static






urlpatterns = [
    path('', views.med_inventory_dash, name='med_inventory_dash'),
    path('medicine/cards/', views.view_medicine_cards, name='medicine_cards'),
    path('medicine/table/', views.view_medicine_table, name='medicine_table'),
    path('create/', views.create_medicine, name='medicine_create'),
    path('update/<int:id>/', views.update_medicine, name='medicine_update'),
    path('delete/<int:id>/', views.delete_medicine, name='medicine_delete'),
    path('export/csv/', views.export_medicine_csv, name='export_medicine_csv'),
    path('export/pdf/', views.export_medicine_pdf, name='export_medicine_pdf'),
    # Remove this line: path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)