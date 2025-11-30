from django.utils import timezone
from django.db import models
from rest_framework.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"


# === Farmer model ===
class Farmer(models.Model):
    farmer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    # Optional extra fields specific to farmers
    #farm_location = models.CharField(max_length=200, blank=True, null=True)
    #land_size = models.FloatField(blank=True, null=True)
    #crops_grown = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Farmer: {self.user.name}"


# === Customer model ===
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    discount_sensitivity = models.FloatField(default=0.0) # E.g., Avg discount of purchased items
    price_elasticity = models.FloatField(default=0.0)     # E.g., Avg price of purchased items
    stock_urgency = models.FloatField(default=0.0)        # E.g., Purchases when stock is low
    
    last_profiled = models.DateTimeField(null=True, blank=True)
    # Optional extra fields specific to customers
    #address = models.CharField(max_length=200, blank=True, null=True)
    #phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Customer: {self.user.name}"
    
class Product(models.Model):
    farmer = models.ForeignKey("Farmer", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    reap_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.farmer.user.name})"



class Market(models.Model):
    farmer = models.ForeignKey("Farmer", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    weight = models.FloatField()
    stock = models.IntegerField()
    discount = models.FloatField(default=0)
    price = models.FloatField()  # calculated in ViewSet
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name} by {self.farmer.user.name}"


# === Automatic creation using signals ===
@receiver(post_save, sender=Users)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'farmer':
            Farmer.objects.create(user=instance)
        elif instance.role == 'customer':
            Customer.objects.create(user=instance)



class WeatherData(models.Model):
    date = models.DateField(unique=True)
    temperature = models.FloatField()
    cloudcover = models.FloatField()
    precipitation = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.temperature}°C"
    
class WeatherPrediction(models.Model):
    date = models.DateField(unique=True)
    temperature = models.FloatField()
    cloudcover = models.FloatField()
    precipitation = models.FloatField()

    def __str__(self):
        return f"Prediction {self.date}"
    
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.cart_id} for Customer {self.customer.customer_id}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )
    market_item = models.ForeignKey(
        Market,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.market_item.product_name} x {self.quantity}"


class CustomerAction(models.Model):
    ACTIONS = [
        ('ADD', 'Add to Cart'),
        ('REMOVE', 'Remove from Cart'),
        ('PURCHASE', 'Purchase')
    ]
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=ACTIONS)
    quantity = models.PositiveIntegerField(default=1)
    price_at_action = models.DecimalField(max_digits=10, decimal_places=2)
    discount_at_action = models.DecimalField(max_digits=5, decimal_places=2)
    stock_at_action = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop} {self.quantity}"
    
class CustomerRecommendation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)
    purchase_prob = models.FloatField()

    class Meta:
        unique_together = ("customer", "crop")
        ordering = ["-purchase_prob"]

    def __str__(self):
        return f"{self.customer.user.name} - {self.crop} ({self.purchase_prob:.2f})"

class CropPrices(models.Model):
    crop = models.CharField(max_length=100)
    year = models.IntegerField()
    predicted_yield = models.FloatField()
    synthetic_price = models.FloatField()  # default if missing
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop} ({self.year})"
    
class DailyCropForecast(models.Model):
    crop = models.CharField(max_length=100)
    date = models.DateField()
    price_estimate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop} - {self.date}"