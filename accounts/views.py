from django.shortcuts import render, redirect
from .models import User, Invitation
# Create your views here.


def registration_view(request):


    ROLE_TEMPLATES = {
        User.Role.ADMIN: 'registration/admin_sign_up.html',
        User.Role.CUSTOMER: 'registration/customer_sign_up.html',
        User.Role.VENDOR: 'registration/vendor_sign_up.html'
    }


    token = request.GET.get('token', '')
    if request.method == 'POST': pass
