from django.urls import path, re_path
from .views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
   ),
   public=False,
   permission_classes=(permissions.IsAdminUser ,),
)

urlpatterns = [   
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),   
    path('company/',CompanyApiView.as_view(),name='card-list'),
    path('disclosures/<int:pk>/', DisclosuresDetailApiView.as_view(), name='card-detail'),
    path('disclosures/',DisclosuresApiView.as_view(),name='disclosures-list'),
    path('add-company/',AddCompanyApiView.as_view(),name='add-company'),
    path('add-disclosures/',AddDisclosuresView.as_view(),name='add-disclosures'),
    path('api/update-disclosure-status/<int:id>/', UpdateDisclosureStatusApiView.as_view(), name='update-disclosure-status'),
    path('nodes/', TreeNodeListAPIView.as_view(), name='tree_nodes'),
   #  path('page-visit/', PageVisitView.as_view(), name='page-visit'),
   #  path('ping/', PingView.as_view(), name='ping'),
   #  path('active-users/', ActiveUsersView.as_view(), name='active_users'),
   #  path('filter/',FilterApiView.as_view(),name='filter'),
   #  path('news/',NewsApiview.as_view(),name='news'),
   #  path('shop-product/',ShopProductApiView.as_view(),),
   #  path('auction_item/',AuctionItemApiView.as_view(),name='auction_item'),
   #  path('news-detail/<int:pk>/',NewsDetailApiView.as_view(),name='news-detail'),
   #  path('contact/',ContactApiview.as_view(),name='contact'),
]