from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from .models import User, Invitation
# Create your views here.



def home(request):
    return render(request, 'accounts/index.html')



def login(request):
    return render(request, 'accounts/login.html')







def registration_view(request):
    ROLE_TEMPLATES = {
        User.Role.ADMIN: 'registration/admin_sign_up.html',
        User.Role.CUSTOMER: 'registration/customer_sign_up.html',
        User.Role.VENDOR: 'registration/vendor_sign_up.html'
    }


    if request.method == 'GET': 
        token = request.GET.get('token', '')
        if not token:
            return render(request, ROLE_TEMPLATES[User.Role.CUSTOMER])

        try:
            invitation = Invitation.objects.get(token=token)
        except (Invitation.DoesNotExist, ValidationError):
            raise
        
        if not invitation.is_valid():
            return redirect('accounts:invalid_invite')

        context = {
            'token': token
        }

        registration_role = invitation.role
        return render(request, ROLE_TEMPLATES[registration_role])









def invalid_invite(request):
    return render(request, 'errors/invalid_invite.html')


