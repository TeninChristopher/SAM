from rest_framework import viewsets, permissions, status
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from services.market_search import get_preferred_market_items
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from services.fetch_weather import fetch_and_save_weather
from ml_model.weather_predictor import predict_next_7_days
from django.shortcuts import render
from .models import *
from .serializers import *
import datetime
from services.recommendations import get_customer_recommendations
import numpy as np



class UserViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Users.objects.all()
    serializer_class = UsersSerializers

    def list(self, request):
        queryset = Users.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        
        
class FarmerViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # ===== List / Retrieve farmer_id using user_id =====
    def list(self, request):
        user_id = request.query_params.get("user_id")
        if user_id:
            # Existing behavior: return single farmer_id for the given user_id
            farmer = Farmer.objects.filter(user__user_id=user_id).first()
            if not farmer:
                return Response({"error": "Farmer not found"}, status=404)
            return Response({"farmer_id": farmer.farmer_id})

        # New behavior: return all farmers
        farmers = Farmer.objects.all()
        serializer = FarmerSerializer(farmers, many=True)
        return Response(serializer.data)

    # ===== Retrieve farmer details by primary key (farmer_id) =====
    def retrieve(self, request, pk=None):
        farmer = Farmer.objects.filter(farmer_id=pk).first()
        if not farmer:
            return Response({"error": "Farmer not found"}, status=404)

        serializer = FarmerSerializer(farmer)
        return Response(serializer.data)

    # ===== Update farmer details by primary key (farmer_id) =====
    def update(self, request, pk=None):
        farmer = Farmer.objects.filter(farmer_id=pk).first()
        if not farmer:
            return Response({"error": "Farmer not found"}, status=404)

        data = request.data
        # Update related user fields
        if "name" in data:
            farmer.user.name = data["name"]
        if "email" in data:
            farmer.user.email = data["email"]
        if "password" in data:
            farmer.user.set_password(data["password"])  # hash password properly

        farmer.user.save()
        farmer.save()

        serializer = FarmerSerializer(farmer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarketViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # ---------------- LIST ----------------
    def list(self, request):
        farmer_id = request.query_params.get("farmer_id")
        items = Market.objects.filter(farmer_id=farmer_id) if farmer_id else Market.objects.all()

        serializer = MarketSerializer(items, many=True)
        return Response(serializer.data)

    # ---------------- CREATE ----------------
    def create(self, request):
        farmer = request.data.get("farmer")
        product = request.data.get("product")
        product_name = request.data.get("product_name")
        weight = float(request.data.get("weight"))
        stock = int(request.data.get("stock"))
        discount = float(request.data.get("discount"))

        # ---------------- 1) Try ML Price ----------------
        crop_price_obj = CropPrices.objects.filter(
            crop__iexact=product_name
        ).order_by("-year").first()

        if crop_price_obj:
            base_price = float(crop_price_obj.synthetic_price)
        else:
            # ---------------- 2) Fallback = avg price × random 0.9–1.2 ----------------
            from django.db.models import Avg
            avg = CropPrices.objects.aggregate(avg=Avg("synthetic_price"))["avg"]

            if avg:
                import random
                base_price = float(avg) * random.uniform(0.9, 1.2)
            else:
                base_price = 10  # final fallback

        # ---------------- Final price ----------------
        final_price = round(base_price * weight * (1 - discount / 100), 2)

        # ---------------- Validate stock ----------------
        try:
            prod = Product.objects.get(id=product)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        total_weight_needed = weight * stock

        if prod.quantity < total_weight_needed:
            return Response({
                "error": f"Not enough stock. Available: {prod.quantity} kg"
            }, status=400)

        # Deduct
        prod.quantity -= total_weight_needed
        prod.save()

        # ---------------- Save Market Item ----------------
        data = {
            "farmer": farmer,
            "product": product,
            "product_name": product_name,
            "weight": weight,
            "stock": stock,
            "discount": discount,
            "price": final_price,
        }

        serializer = MarketSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)

    # ---------------- DELETE ----------------
    def destroy(self, request, pk=None):
        try:
            item = Market.objects.get(pk=pk)
        except Market.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        # restore product quantity
        try:
            prod = Product.objects.get(id=item.product_id)
            prod.quantity += item.weight * item.stock
            prod.save()
        except Product.DoesNotExist:
            pass

        item.delete()
        return Response({"message": "Deleted successfully"}, status=204)
    

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        farmer_id = self.request.query_params.get("farmer_id")
        qs = Product.objects.all()
        if farmer_id:
            qs = qs.filter(farmer_id=farmer_id)
        return qs

    def create(self, request, *args, **kwargs):
        farmer_id = request.data.get('farmer')
        name = request.data.get('name')
        quantity = float(request.data.get('quantity', 0))
        reap_date = request.data.get('reap_date')

        # Check if this farmer already has this crop + reap_date
        product = Product.objects.filter(
            farmer_id=farmer_id,
            name__iexact=name,
            reap_date=reap_date
        ).first()

        if product:
            # Sum quantity
            product.quantity += quantity
            product.save()
        else:
            # Create new product
            product = Product.objects.create(
                farmer_id=farmer_id,
                name=name,
                quantity=quantity,
                reap_date=reap_date
            )

        serializer = self.get_serializer(product)
        return Response(serializer.data)
    

class CustomerViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        user_id = request.GET.get("user_id")

        # No filter → list all customers
        if not user_id:
            queryset = Customer.objects.all()
            serializer = CustomerSerializers(queryset, many=True)
            return Response(serializer.data)

        # Filter by user_id → return single customer
        try:
            customer = Customer.objects.get(user__user_id=user_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        # Auto-create cart due to OneToOne link
        cart, created = Cart.objects.get_or_create(customer=customer)

        # Response for single-customer fetch
        return Response({
            "customer_id": customer.customer_id,
            "user_id": user_id,
            "email": customer.user.email,
            "cart_id": cart.cart_id,
            "name": customer.user.name if hasattr(customer.user, "name") else "",
        })
    
class LoginView(APIView):
    """Login view without decorators"""
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.password != password:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UsersSerializers(user)
        return Response({'message': 'Login successful', 'user': serializer.data}, status=status.HTTP_200_OK)
    

class WeatherDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer

    def list(self, request):
        queryset = WeatherData.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class WeatherAPI(APIView):
    def get(self, request):
        # Fetch & store today's real data
        fetch_and_save_weather()

        # Run ML prediction & store in DB
        prediction = predict_next_7_days()

        latest = WeatherData.objects.latest("date")
        pred_data = WeatherPrediction.objects.all().order_by("date")

        return Response({
            "current_weather": WeatherDataSerializer(latest).data,
            "next_7_days": WeatherPredictionSerializer(pred_data, many=True).data
        })

@api_view(['GET'])
def get_weather(request):
    try:
        current = WeatherData.objects.latest('date')
        current_weather = {
            "id": 1,
            "date": current.date,
            "temperature": current.temperature,
            "cloudcover": current.cloudcover,
            "precipitation": current.precipitation
        }
    except WeatherData.DoesNotExist:
        current_weather = None

    predictions = WeatherPrediction.objects.order_by('date')[:7]
    next_7_days = [
        {
            "id": i+1,
            "date": p.date,
            "temperature": p.temperature,
            "cloudcover": p.cloudcover,
            "precipitation": p.precipitation
        }
        for i, p in enumerate(predictions)
    ]

    return Response({
        "current_weather": current_weather,
        "next_7_days": next_7_days
    })


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    # ============================================================
    # ADD ITEM TO CART
    # ============================================================
    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        market_item_id = request.data.get("market_item_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            market_item = Market.objects.get(id=market_item_id)
        except Market.DoesNotExist:
            return Response({"error": "Market item not found"}, status=404)

        existing_cart_item = CartItem.objects.filter(
            cart=cart, market_item=market_item
        ).first()

        total_quantity = quantity + (existing_cart_item.quantity if existing_cart_item else 0)

        if total_quantity > market_item.stock:
            return Response(
                {"error": f"Cannot add more than available stock ({market_item.stock})"},
                status=400
            )

        if existing_cart_item:
            existing_cart_item.quantity = total_quantity
            existing_cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart, market_item=market_item, quantity=quantity
            )

        # Log ADD action
        CustomerAction.objects.create(
            customer_id=cart.customer,
            crop=market_item.product_name,
            action="ADD",
            quantity=quantity,
            price_at_action=market_item.price,
            discount_at_action=market_item.discount,
            stock_at_action=market_item.stock,
            timestamp=timezone.now()
        )

        return Response(CartSerializer(cart).data)

    # ============================================================
    # UPDATE QUANTITY
    # ============================================================
    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get("item_id")
        new_quantity = int(request.data.get("quantity"))

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        old_quantity = item.quantity

        if new_quantity > item.market_item.stock:
            return Response({"error": "Not enough stock"}, status=400)

        # Determine ADD / REMOVE
        if new_quantity > old_quantity:
            action_type = "ADD"
            action_qty = new_quantity - old_quantity
        elif new_quantity < old_quantity:
            action_type = "REMOVE"
            action_qty = old_quantity - new_quantity
        else:
            return Response(CartSerializer(cart).data)

        # Save
        item.quantity = new_quantity
        item.save()

        # Log action
        CustomerAction.objects.create(
            customer_id=cart.customer,
            crop=item.market_item.product_name,
            action=action_type,
            quantity=action_qty,
            price_at_action=item.market_item.price,
            discount_at_action=item.market_item.discount,
            stock_at_action=item.market_item.stock,
            timestamp=timezone.now()
        )

        return Response(CartSerializer(cart).data)

    # ============================================================
    # REMOVE ITEM
    # ============================================================
    @action(detail=True, methods=["delete"])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get("item_id")

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        # Log action
        CustomerAction.objects.create(
            customer_id=cart.customer,
            crop=item.market_item.product_name,
            action="REMOVE",
            quantity=item.quantity,
            price_at_action=item.market_item.price,
            discount_at_action=item.market_item.discount,
            stock_at_action=item.market_item.stock,
            timestamp=timezone.now()
        )

        item.delete()
        return Response(CartSerializer(cart).data)

    # ============================================================
    # PURCHASE (UPDATED)
    # ============================================================
    @action(detail=True, methods=["post"])
    def purchase(self, request, pk=None):
        cart = self.get_object()
        customer = cart.customer

        items = cart.items.all()

        if not items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # 1️⃣ Collect invalid items
        invalid_items = []
        for item in items:
            if item.quantity > item.market_item.stock:
                invalid_items.append({
                    "product": item.market_item.product_name,
                    "requested": item.quantity,
                    "stock": item.market_item.stock
                })

        # 2️⃣ Stop purchase if any invalid items
        if invalid_items:
            return Response({
                "error": "Some items have insufficient stock.",
                "invalid_items": invalid_items
            }, status=400)

        # 3️⃣ Purchase valid items
        purchased_items = []
        for item in items:
            market_item = item.market_item

            # Reduce stock
            market_item.stock -= item.quantity
            market_item.save()

            # Log PURCHASE action
            CustomerAction.objects.create(
                customer_id=customer,
                crop=market_item.product_name,
                action="PURCHASE",
                quantity=item.quantity,
                price_at_action=market_item.price,
                discount_at_action=market_item.discount,
                stock_at_action=market_item.stock,
                timestamp=timezone.now()
            )

            purchased_items.append({
                "product": market_item.product_name,
                "qty": item.quantity
            })

            # Remove purchased item from cart
            item.delete()

        return Response({
            "success": True,
            "message": "Purchase successful!",
            "purchased_items": purchased_items
        }, status=200)

class CustomerActionViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerActionSerializer
    queryset = CustomerAction.objects.all()


def log_customer_action(customer, crop_name, action, quantity, price, discount, stock):
    CustomerAction.objects.create(
        customer_id=customer,
        crop=crop_name,
        action=action,
        quantity=quantity,
        price_at_action=price,
        discount_at_action=discount,
        stock_at_action=stock
    )

class CustomerRecommendationViewSet(viewsets.ViewSet):
    # ... permission classes ...

    def list(self, request):
        # The frontend MUST send ?customer_id=123 for the DB to update
        customer_id = request.query_params.get('customer_id', None)

        if customer_id:
            try:
                # Ensure you get the OBJECT, not the ID
                customer = Customer.objects.get(pk=customer_id)
                
                # This function (from step 1) updates the DB
                get_customer_recommendations(customer)
                
                # Retrieve the updated rows
                recommendations = CustomerRecommendation.objects.filter(customer=customer).order_by('-purchase_prob')[:10]
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)
        else:
            # This path reads OLD data only
            recommendations = CustomerRecommendation.objects.all().order_by('-purchase_prob')[:10]

        serializer = CustomerRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

@require_http_methods(["GET"])
def preferred_market_items_api(request, customer_id):
    """
    API endpoint to fetch market items recommended for a specific customer.
    """
    try:
        # 1. Call the service function to get the structured list of preferred items
        preferred_items_list = get_preferred_market_items(
            customer_id=customer_id, 
            limit=20
        )
        
        # 2. Return the list as a JSON response
        return JsonResponse({
            'success': True,
            'data': preferred_items_list,
            'customer_id': customer_id
        })
        
    except Exception as e:
        # 3. Handle errors gracefully
        import traceback
        print(f"API Error fetching preferred items: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


DEFAULT_PRICE = 1000.0

class CropPricesViewSet(viewsets.ModelViewSet):
    queryset = CropPrices.objects.all()
    serializer_class = CropPricesSerializer

    def list(self, request, *args, **kwargs):
        """Override list to include synthetic prices + 7-day daily forecasts."""
        queryset = self.get_queryset()
        response_data = []

        # Serialize initial data
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # ---------------------------------------
        # 1) Compute average synthetic price
        # ---------------------------------------
        prices = [row['synthetic_price'] for row in data if row['synthetic_price'] is not None]
        average_price = np.mean(prices) if prices else DEFAULT_PRICE

        today = datetime.date.today()

        for row in data:
            crop_name = row["crop"]

            # ---------------------------------------
            # 2) Fill missing synthetic price
            # ---------------------------------------
            if row['synthetic_price'] is None:
                random_factor = np.random.uniform(0.95, 1.05)
                row['synthetic_price'] = round(average_price * random_factor, 2)

            # ---------------------------------------
            # 3) Fill missing predicted yield
            # ---------------------------------------
            if row['predicted_yield'] is None:
                row['predicted_yield'] = 0.0

            base_price = row['synthetic_price']

            # ---------------------------------------
            # 4) Ensure 7-day forecast exists
            # ---------------------------------------
            existing = DailyCropForecast.objects.filter(
                crop=crop_name,
                date__gte=today
            ).order_by("date")

            # If fewer than 7 forecast records → regenerate
            if existing.count() < 7:
                DailyCropForecast.objects.filter(crop=crop_name).delete()

                for i in range(1, 8):
                    date = today + datetime.timedelta(days=i)
                    price = round(base_price * (0.95 + np.random.rand() * 0.1), 2)

                    DailyCropForecast.objects.create(
                        crop=crop_name,
                        date=date,
                        price_estimate=price,
                    )

                # Reload data
                existing = DailyCropForecast.objects.filter(
                    crop=crop_name,
                    date__gte=today
                ).order_by("date")

            # ---------------------------------------
            # 5) Attach forecast to the output
            # ---------------------------------------
            row["forecast_7_days"] = [
                {
                    "date": str(f.date),
                    "price_estimate": f.price_estimate
                }
                for f in existing[:7]
            ]

            response_data.append(row)

        return Response(response_data)
    
class DailyCropForecastViewSet(viewsets.ModelViewSet):
    queryset = DailyCropForecast.objects.all().order_by('date')
    serializer_class = DailyCropForecastSerializer

    def list(self, request, *args, **kwargs):
        crop_name = request.query_params.get('crop')

        queryset = self.get_queryset()
        if crop_name:
            queryset = queryset.filter(crop=crop_name).order_by('date')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
