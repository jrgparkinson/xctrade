"""xctrade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, re_path
from trading import views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/oauth/(?P<backend>[^/]+)/$', views.exchange_token),
    re_path(r'^api/athletes/$', views.athletes_list),
    # re_path(r'^api/athletes/([0-9])$', views.athletes_detail),
    re_path(r'^api/orders/$', views.orders_list),
    re_path(r'^api/entities/$', views.entities_list),
    re_path(r'^api/orders/(?P<pk>[0-9]+)/$', views.orders_detail),
    re_path("googleafce55136e9c6cd8.html", TemplateView.as_view(template_name='googleafce55136e9c6cd8.html')),
    re_path(".*", TemplateView.as_view(template_name='index.html')),
]
