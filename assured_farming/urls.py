from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from core.admin_dashboard import admin_dashboard
from django.views.generic import RedirectView  # 👈 add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/marketplace/', include('marketplace.urls')),
    path('api/v1/contracts/', include('contracts.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/analytics/', include('analytics.urls')),

    # 👇 Redirect root ("/") to Swagger UI
    path('', RedirectView.as_view(url='/api/v1/schema/swagger-ui/', permanent=False)),
]
