from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    SignUpAPIView,
    TitleViewSet,
    TokenApiView,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpAPIView.as_view()),
    path('v1/auth/token/', TokenApiView.as_view()),
]
