from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import User, Invitation
# Create your views here.


def registration_view(request):
    ROLE_TEMPLATES = {
        User.Role.ADMIN: 'registration/admin_sign_up.html',
        User.Role.CUSTOMER: 'registration/customer_sign_up.html',
        User.Role.VENDOR: 'registration/vendor_sign_up.html'
    }


    if request.method == 'GET': 
        token = request.GET.get('token', '')
        if not token:
            role = User.Role.CUSTOMER
            return render(request, ROLE_TEMPLATES.get(role))

        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            raise
        
        if invitation.is_valid():
            role = invitation.role
            return render(request, ROLE_TEMPLATES.get(role))
        else:
            raise PermissionDenied('The invitaion token has either expired or has been\
                                    used already. Please contact admin for support')




    if request.method == 'POST': pass
