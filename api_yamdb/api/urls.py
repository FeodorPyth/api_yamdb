from django.urls import include, path
from rest_framework.routers import DefaultRouter


from api.views import (
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    SignUpAPIView,
    TokenView,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpAPIView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
]
