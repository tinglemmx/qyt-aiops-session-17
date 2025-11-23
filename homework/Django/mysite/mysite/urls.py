"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from viewers.index import index
from viewers.my_login import my_login, my_logout

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path('devices/', include('devices.urls')),
    path("dashboard/", include("dashboard.urls")),
    path('accounts/login/', my_login, name='qyt_login'),     #accounts/login/是固定的url
    path('accounts/logout/', my_logout, name='qyt_logout'),  #accounts/logout/是固定的url
]
