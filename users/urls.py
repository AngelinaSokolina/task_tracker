from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomTokenObtainPairView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("", include(router.urls)),
]
