from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ===========================
# Custom User Model with Role
# ===========================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant'),
        ('delivery', 'Delivery Agent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.first_name or self.username} ({self.role})"


# ===========================
# Restaurant Model
# ===========================
class Restaurant(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# ===========================
# Menu Item Model
# ===========================
class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_item_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# ===========================
# Order Model
# ===========================
class Order(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"



# ===========================
# Order Item Model
# ===========================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (Order #{self.order.id})"
