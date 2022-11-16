"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from .views import place_order,payments,order_complete,order_failed
urlpatterns = [
    path('place_order/',place_order,name='place_order'),
    path('payments/',payments,name='payments'),
    path('order_complete/',order_complete,name='order_complete'),
    path('order_failed/',order_failed,name='order_failed'),
    #path('app_callback/',app_callback,name='app_callback'),
]
