from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='poly_crud:welcome'), name='logout'),
    path('register/', views.register, name='register'),
]