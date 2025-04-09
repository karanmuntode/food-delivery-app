from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Restaurant, MenuItem, Order, OrderItem
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# ===============================
# User Serializer with Password Hashing
# ===============================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role  # Include user's role in token response
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

# ===============================
# Restaurant Serializer with Owner Details
# ===============================
class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'owner_email', 'name', 'description', 'image']

    def get_owner_email(self, obj):
        return obj.owner.email

# ===============================
# Menu Item Serializer
# ===============================
class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant', 'restaurant_name', 'name', 'description', 'price', 'image']

# ===============================
# Order Item Serializer
# ===============================
class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'item_id', 'quantity']

# ===============================
# Order Serializer with nested OrderItems
# ===============================
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'status', 'created_at', 'items', 'customer_name']
        read_only_fields = ['customer', 'created_at']

    def get_customer_name(self, obj):
        return obj.customer.first_name or obj.customer.username

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
