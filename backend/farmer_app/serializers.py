from rest_framework import serializers
from .models import *

class UsersSerializers(serializers.ModelSerializer):
    class Meta:
        model=Users
        fields = '__all__'


class FarmerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=False)
    email = serializers.EmailField(source="user.email", read_only=False)
    password = serializers.CharField(source="user.password", write_only=True)

    class Meta:
        model = Farmer
        fields = ['farmer_id', 'name', 'email', 'password']


class ProductSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.user.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'farmer', 'farmer_name', 'name', 'quantity', 'reap_date']


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = [
            'id',
            'farmer',
            'product',
            'product_name',
            'weight',     # <-- correct field
            'stock',
            'discount',
            'price',
            'date_added'
        ]


class CustomerSerializers(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields = '__all__'

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=WeatherData
        fields = "__all__"

class WeatherPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherPrediction
        fields = "__all__"

class CartItemSerializer(serializers.ModelSerializer):
    cart_item_id = serializers.IntegerField(source="id", read_only=True)
    product_name = serializers.CharField(source="market_item.product_name", read_only=True)
    price = serializers.FloatField(source="market_item.price", read_only=True)
    total_price = serializers.SerializerMethodField()

    # ⭐ Add nested market_item field
    market_items = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "cart_item_id",
            "product_name",
            "price",
            "quantity",
            "total_price",
            "market_items",
        ]

    def get_market_items(self, obj):
        return {
            "id": obj.market_item.id,
            "stock": obj.market_item.stock,
            "price": obj.market_item.price,
            "discount": obj.market_item.discount,
        }

    def get_total_price(self, obj):
        return obj.quantity * obj.market_item.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["cart_id", "customer", "items", "total_price"]  # cart_id exists in model, no source needed

    def get_total_price(self, obj):
        return sum(item.quantity * item.market_item.price for item in obj.items.all())
    

class CustomerActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAction
        fields = "__all__"


class CustomerRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerRecommendation
        fields = '__all__'


class CropPricesSerializer(serializers.ModelSerializer):
    forecast_7_days = serializers.SerializerMethodField()

    class Meta:
        model = CropPrices
        fields = [
            "id",
            "crop",
            "year",
            "synthetic_price",
            "predicted_yield",
            "forecast_7_days",
        ]

    def get_forecast_7_days(self, obj):
        forecasts = DailyCropForecast.objects.filter(crop=obj.crop).order_by("date")[:7]
        return [
            {
                "date": f.date,
                "price_estimate": f.price_estimate
            }
            for f in forecasts
        ]

class DailyCropForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCropForecast
        fields = ['id', 'crop', 'date', 'price_estimate', 'created_at']
