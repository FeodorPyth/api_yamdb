from django.urls import include, path
from rest_framework import routers

from .views import SignUpAPIView, TokenView, UserViewSet


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', SignUpAPIView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(router_v1.urls)),
]
