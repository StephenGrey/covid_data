"""my_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import urls
from django.http import HttpResponseRedirect

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graph/', include('graph.urls')),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(),name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^accounts/password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^accounts/password/reset/confirm/$', 
             auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', 
             auth_views.PasswordResetCompleteView.as_view(), name='password_reset_done'),
]
