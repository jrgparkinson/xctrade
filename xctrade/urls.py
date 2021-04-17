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

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions 

schema_view = get_schema_view(
   openapi.Info(
      title="XCTrade API",
      default_version='v1',
      description="API for interacting with the XCTrade game engine.",
    #   terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="jamie.parkinson@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# TODO: rewrite endpoints like
# auction_shares => auction/<pk>/shares/

urlpatterns = [
    path("admin/", admin.site.urls),

    re_path(r"^api/oauth/(?P<backend>[^/]+)/$", views.exchange_token),
    re_path(r"^api/athletes/$", views.athletes_list),
    re_path(r"^api/athletes/(?P<pk>[0-9]+)/$", views.athlete_detail),
    re_path(r"^api/orders/$", views.orders_list),
    re_path(r"^api/entities/$", views.entities_list),
    re_path(r"^api/profile/$", views.profile),
    re_path(r"^api/shares/$", views.shares_list),
    re_path(r"^api/trades/$", views.trades_list),
    re_path(r"^api/races/$", views.races_list),
    re_path(r"^api/results/$", views.results_list),
    re_path(r"^api/dividends/$", views.dividends_list),
    re_path(r"^api/loans/$", views.loans_list),
    re_path(r"^api/loan_info/$", views.loan_info),
    re_path(r"^api/loans/(?P<pk>[0-9]+)/$", views.loan_detail),
    re_path(r"^api/auction/$", views.active_auction),
    re_path(r"^api/auction_shares/$", views.auction_shares),
    re_path(r"^api/bids/(?P<auction_pk>[0-9]+)/$", views.bids_list),
    re_path(r"^api/races/(?P<pk>[0-9]+)/$", views.races_detail),
    re_path(r"^api/orders/(?P<pk>[0-9]+)/$", views.orders_detail),
    re_path(r"^api/order_prices/(?P<athlete_pk>[0-9]+)/$", views.order_prices),

    re_path(
        "googleafce55136e9c6cd8.html",
        TemplateView.as_view(template_name="googleafce55136e9c6cd8.html"),
    ),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r"^swagger/$", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),




    re_path(".*", TemplateView.as_view(template_name="index.html")),
]
