from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name="logout"),
    path('verify-account/', views.verify_account_view, name='verify_account'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('subscribe/', views.subscribe, name="subscribe"),
    path('afterbill/', views.afterbill, name='afterbill'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

