"""Admin dashboard view for KYC approvals, disputes, and contracts requiring attention."""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import KYCDocument, User
from contracts.models import Dispute, Contract


def is_admin_user(user):
    return user.is_staff or user.role == 'admin'


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Dashboard showing pending KYCs, disputes, and contracts needing attention."""
    pending_kycs = KYCDocument.objects.filter(status='pending').select_related('user')[:10]
    open_disputes = Dispute.objects.filter(status__in=['open', 'under_review']).select_related('contract')[:10]
    pending_contracts = Contract.objects.filter(status__in=['proposed', 'accepted']).select_related('listing', 'buyer')[:10]
    
    context = {
        'pending_kycs': pending_kycs,
        'open_disputes': open_disputes,
        'pending_contracts': pending_contracts,
    }
    return render(request, 'admin/dashboard.html', context)
