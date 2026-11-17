from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from habits.views import HabitViewSet, PublicHabitListAPIView
from users.views import UserRegisterAPIView

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("admin/", admin.site.urls),

    
    path("api/users/register/", UserRegisterAPIView.as_view(), name="register"),
    path("api/users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


    path("api/habits/public/", PublicHabitListAPIView.as_view(), name="public_habits"),
    path("api/", include(router.urls)),


    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
