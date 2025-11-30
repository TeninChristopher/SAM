from farmer_app.models import Customer, CustomerRecommendation
from farmer_app.models import Market # FIX: Import Market from farmer_app.models
from django.db.models import Prefetch, Q

def get_preferred_market_items(customer_id, limit=20):
    """
    Retrieves market items based on a customer's stored recommendations,
    prioritizing products with higher purchase probability.

    Args:
        customer_id (int): The primary key of the Customer.
        limit (int): The maximum number of market items to return.

    Returns:
        list: A list of dictionaries representing the Market objects, 
              ordered by preference score, ready for JSON serialization.
    """
    try:
        # 1. Fetch the customer and their most recent recommendations
        customer = Customer.objects.prefetch_related(
            Prefetch(
                'customerrecommendation_set',
                queryset=CustomerRecommendation.objects.order_by('-purchase_prob'),
                to_attr='recommendations'
            )
        ).get(pk=customer_id)
        
    except Customer.DoesNotExist:
        print(f"ERROR: Customer ID {customer_id} not found.")
        return []

    # Check if recommendations have been run
    if not customer.recommendations:
        print(f"INFO: Customer {customer_id} has no recommendations yet. Returning empty list.")
        return []

    # 2. Get the list of recommended crops and their probabilities
    recommended_crops = {rec.crop: rec.purchase_prob for rec in customer.recommendations}
    crop_names = list(recommended_crops.keys())

    # 3. Build a query to find matching Market items
    # Filter Market listings where the product_name is in the list of recommended crops.
    market_items = Market.objects.filter(
        product_name__in=crop_names,
        stock__gt=0 # Only show items that are actually in stock
    ).select_related('farmer__user', 'product') # Optimize joins

    # 4. Sort the Market items based on the recommendation score (this is done in Python/memory)
    def sort_key(item):
        """Sorts market items based on the stored purchase probability for that crop."""
        # Use the probability, defaulting to 0 if the crop somehow wasn't in the recs list
        probability = recommended_crops.get(item.product_name, 0)
        return probability

    # Convert queryset to list and sort
    sorted_items = sorted(list(market_items), key=sort_key, reverse=True)

    # 5. Prepare data for JSON serialization and return the top N preferred items
    preferred_data = []
    for item in sorted_items[:limit]:
        # Extract fields needed for the frontend
        preferred_data.append({
            'id': item.pk,
            'crop_name': item.product_name,
            'price': item.price,
            'weight': item.weight,
            'stock': item.stock,
            'discount': item.discount,
            # Assuming user.name exists and is linked through the Farmer model
            'farmer_name': item.farmer.user.name, 
            'purchase_probability': round(recommended_crops.get(item.product_name, 0), 4),
        })

    return preferred_data