from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignUpAPIView,
    TitleViewSet,
    TokenApiView,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(
    r'titles',
    TitleViewSet,
    basename='title'
)
router_v1.register(
    r'categories',
    CategoryViewSet,
    basename='category'
)
router_v1.register(
    r'genres',
    GenreViewSet,
    basename='genre'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register(
    r'users',
    UserViewSet,
    basename='user'
)

auth_urls = [
    path('signup/', SignUpAPIView.as_view()),
    path('token/', TokenApiView.as_view()),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_urls)),
]
