from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),
    path('invalid-invite/', views.invalid_invite, name='invalid_invite'),
    path('register/', views.registration_view, name='registration'),
    path('login/', views.login, name='login')
]