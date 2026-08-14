from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('security-question/', views.security_question_view, name='security_question'),
    path('signup/', views.signup_view, name='signup'),
    path('loading-auth/', views.loading_auth_view, name='loading_auth'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-external-account/', views.add_external_account_view, name='add_external_account'),
    path('contact/', views.contact_view, name='contact'),
    path('debit-cards/', views.debit_cards_view, name='debit_cards'),
    path('logout/', views.logout_view, name='logout'),
]