from rest_framework import viewsets, permissions, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model

from .models import Restaurant, MenuItem, Order, OrderItem
from .serializers import (
    UserSerializer,
    RestaurantSerializer,
    MenuItemSerializer,
    OrderSerializer,
    CustomTokenObtainPairSerializer
)

User = get_user_model()

# ✅ Public User Registration Endpoint
class RegisterView(APIView):
    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role", "customer")

        if User.objects.filter(username=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ['customer', 'restaurant']:
            return Response({"error": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            role=role
        )
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

# ✅ Restaurant Owner Registration Endpoint
class RegisterRestaurantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# ✅ Restaurant ViewSet (Owner-only for create/view)
class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Restaurant.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ✅ Menu Item ViewSet
class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'restaurant':
            restaurant = Restaurant.objects.filter(owner=user).first()
            if restaurant:
                return MenuItem.objects.filter(restaurant=restaurant)
        return MenuItem.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = Restaurant.objects.filter(owner=user).first()
        if restaurant:
            serializer.save(restaurant=restaurant)
        else:
            raise serializers.ValidationError("You must register a restaurant before uploading dishes.")

# ✅ Public Menu Endpoint
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_menu_by_restaurant(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
        items = MenuItem.objects.filter(restaurant=restaurant)
        return Response({
            "restaurant": RestaurantSerializer(restaurant).data,
            "menu": MenuItemSerializer(items, many=True).data
        })
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found."}, status=404)

# ✅ Orders ViewSet with Nested Order Items
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Order.objects.filter(customer=user)
        elif user.role == 'restaurant':
            if hasattr(user, 'restaurant'):
                return Order.objects.filter(restaurant=user.restaurant)
            return Order.objects.none()
        return Order.objects.none()

    def perform_create(self, serializer):
        # Get the restaurant from the first item (all items must be from same restaurant)
        items = self.request.data.get("items", [])
        if not items:
            raise serializers.ValidationError("No items provided.")

        first_item_id = items[0].get("item_id")
        try:
            item = MenuItem.objects.get(id=first_item_id)
            serializer.save(customer=self.request.user, restaurant=item.restaurant)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Invalid menu item.")

# ✅ Dashboard View
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'customer':
            orders = Order.objects.filter(customer=user)
            serializer = OrderSerializer(orders, many=True)
            return Response({
                "role": "customer",
                "email": user.email,
                "orders": serializer.data
            })

        elif user.role == 'restaurant':
            restaurant = Restaurant.objects.filter(owner=user).first()
            if not restaurant:
                return Response({"role": "restaurant", "restaurant": None})

            menu = MenuItem.objects.filter(restaurant=restaurant)
            orders = Order.objects.filter(restaurant=restaurant)

            return Response({
                "role": "restaurant",
                "restaurant": RestaurantSerializer(restaurant).data,
                "menu": MenuItemSerializer(menu, many=True).data,
                "orders": OrderSerializer(orders, many=True).data
            })

        return Response({"error": "Unsupported role. Contact admin."}, status=400)

# ✅ JWT Token View with Role Included
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
