from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
)

router_v01 = DefaultRouter()
router_v01.register('titles', TitleViewSet, basename='title')
router_v01.register('categories', CategoryViewSet, basename='category')
router_v01.register('genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('v1/', include(router_v01.urls)),
]
