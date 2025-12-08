from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('results/', views.search_results, name='results'),
    path('contact/', views.contact, name='contact'),
    path('payment/', views.payment_page, name='payment'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
