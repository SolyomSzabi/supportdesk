from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import me
from tickets.views import TicketViewSet

from .views import health, spa_index

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/me/", me, name="me"),
    path("api-auth/", include("rest_framework.urls")),
    path("healthz/", health, name="health"),
    # Everything else is a page of the Vue app (must stay last).
    re_path(r"^(?!api/|admin/|api-auth/|static/).*$", spa_index, name="spa"),
]
