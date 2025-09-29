"""pycharmtut URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView

from gadget_communicator_pull import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', TokenObtainPairView.as_view(), name='create-token'),
    path('api/', include('authentication.urls')),
    path('gadget_communicator_pull/', include('gadget_communicator_pull.urls')),
]


