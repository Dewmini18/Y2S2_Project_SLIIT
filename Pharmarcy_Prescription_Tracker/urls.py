from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from accounts.views import CustomLoginView

urlpatterns = [
    # Make login the root URL
    path('', CustomLoginView.as_view(), name='login'),
    
    # Other URLs
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # This includes all URLs from accounts app
    
    # Medicine inventory URLs
    path('medicine/', include('Medicine_inventory.urls')),
    path('prescriptions/', include('prescriptions.prescription_urls')),
    path('non-medical/', include('Non_Medicine_inventory.urls', namespace='non_medicine')),
    path('payments/' , include('payments.payments_urls')),
    path('online-store/', include('onlineStore.urls')),
]

# For serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'django.views.defaults.permission_denied'