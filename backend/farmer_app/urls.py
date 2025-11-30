from django.contrib import admin
from django.urls import path, include
from . import views
from .views import *
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('users', UserViewset, basename='users')
router.register('farmer', FarmerViewset, basename='farmer')
router.register('customer', CustomerViewset, basename='customer')
router.register('weather-data', WeatherDataViewSet, basename='weather-data')
router.register(r'market', MarketViewSet, basename='market')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'customeraction', CustomerActionViewSet, basename='customeraction')
router.register(r'recommendations', CustomerRecommendationViewSet, basename='recommendations')
router.register(r'crop-prices', CropPricesViewSet, basename='crop-prices')
router.register(r'daily-forecast', DailyCropForecastViewSet, basename='daily-forecast')

urlpatterns = [
    path('', include(router.urls)),            # for /users/
    path('login/', LoginView.as_view(), name='login'),  # manual APIView route
    path("weather/", WeatherAPI.as_view(), name='weather'),
    path('api/weather/', get_weather, name='get_weather'),
    path('recommendations/<int:customer_id>/', views.preferred_market_items_api, name='preferred_market_items_api'),
]
