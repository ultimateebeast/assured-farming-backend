from django.urls import path
from . import views

urlpatterns = [
    # Backwards-compatible endpoints used by frontend
    path('dashboard/', views.farmer_revenue, name='dashboard'),
    path('revenue/', views.farmer_revenue, name='revenue'),
    path('farmer-revenue/', views.farmer_revenue, name='farmer-revenue'),
    path('active-contracts/', views.active_contracts, name='active-contracts'),
    path('avg-delivery-time/', views.avg_delivery_time, name='avg-delivery-time'),
    path('acceptance-rate/', views.proposals_acceptance_rate, name='acceptance-rate'),
]
