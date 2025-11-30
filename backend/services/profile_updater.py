from farmer_app.models import CustomerAction, Customer # Assuming CustomerAction is in farmer_app
from django.db.models import Avg
from django.utils import timezone

def update_customer_profile(customer_id):
    """
    Calculates and saves customer preference scores based on ALL past purchases.
    This function should run infrequently (e.g., daily/nightly).
    """
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        # Cannot update profile if customer doesn't exist
        print(f"ERROR: Customer ID {customer_id} not found for profile update.")
        return

    # 1. Get ALL historical purchases for the customer
    purchases = CustomerAction.objects.filter(
        customer_id=customer_id, 
        action='PURCHASE'
    ).exclude(
        # Exclude bad data points
        price_at_action__isnull=True,
        discount_at_action__isnull=True,
        stock_at_action__isnull=True,
    )
    
    # Defaults/Cold Start Profile
    if not purchases.exists():
        customer.discount_sensitivity = 0.5
        customer.price_elasticity = 0.5
        customer.stock_urgency = 0.5
    else:
        # 2. Calculate the preference scores from purchases
        
        # Aggregate the average context of items PURCHASED
        stats = purchases.aggregate(
            avg_disc=Avg('discount_at_action'),
            avg_price=Avg('price_at_action'),
            avg_stock=Avg('stock_at_action'),
        )
        
        # FIX: Explicitly cast the Decimal values returned by Django's Avg
        # to float before using them in calculations with float literals.
        avg_discount = float(stats['avg_disc'] or 0)
        avg_price = float(stats['avg_price'] or 0)
        avg_stock = float(stats['avg_stock'] or 0)

        # 3. Simple Normalization/Mapping (Needs domain tuning, but this is a start)
        # Assuming Max Discount = 30, Max Price = 100, Max Stock = 20
        MAX_DISCOUNT = 30.0
        MAX_PRICE = 100.0
        MAX_STOCK = 20.0 
        
        # Discount Sensitivity: Higher average discount purchased -> Higher sensitivity
        customer.discount_sensitivity = min(avg_discount / MAX_DISCOUNT, 1.0)
        
        # Price Elasticity: Higher average price purchased -> Lower elasticity (less sensitive to price)
        # We invert the score (1 - score) so high elasticity means they buy cheap.
        customer.price_elasticity = 1.0 - min(avg_price / MAX_PRICE, 1.0)
        
        # Stock Urgency: Lower average stock purchased -> Higher urgency
        # We invert the score (1 - score) so high urgency means they buy when stock is low.
        customer.stock_urgency = 1.0 - min(avg_stock / MAX_STOCK, 1.0)
    
    # Save the updated profile and timestamp
    customer.last_profiled = timezone.now()
    customer.save()
    
    return customer.discount_sensitivity, customer.price_elasticity, customer.stock_urgency