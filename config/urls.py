from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Task Tracker API",
        default_version="v1",
        description="Документация для API трекера задач сотрудников",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Обновление JWT-токена
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Документация
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("docs/json/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    # API приложений
    path("api/", include("users.urls")),
    path("api/", include("tasks.urls")),
]
