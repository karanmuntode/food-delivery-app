from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views 
from .views import (
    UserViewSet,
    RestaurantViewSet,
    MenuItemViewSet,
    OrderViewSet,
    RegisterView,
    RegisterRestaurantView,
    DashboardView,
    CustomTokenObtainPairView
)

# 🔄 Register API endpoints using router
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('menu-items', MenuItemViewSet, basename='menuitem')
router.register('orders', OrderViewSet, basename='order')

# 🧭 Define all routes
urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('register-restaurant/', RegisterRestaurantView.as_view(), name='register-restaurant'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # 🔐 Custom JWT Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("public-menu/<int:pk>/", views.public_menu_by_restaurant),
]
