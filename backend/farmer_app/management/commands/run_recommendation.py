from django.core.management.base import BaseCommand
from django.utils import timezone
# Assuming Customer and services are available in the project context
from farmer_app.models import Customer
from services.recommendations import get_customer_recommendations
from services.profile_updater import update_customer_profile # <-- NEW IMPORT

class Command(BaseCommand):
    help = "Run recommendation pipeline for customers directly. Updates profile first."

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer_id',
            type=int,
            help='Run for a specific customer ID'
        )

    def handle(self, *args, **options):
        customer_id = options.get('customer_id')

        self.stdout.write(self.style.WARNING(f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] === STARTING RECOMMENDATION ENGINE ==="))

        if customer_id:
            customers = Customer.objects.filter(pk=customer_id)
            if not customers.exists():
                self.stdout.write(self.style.ERROR(f"No customer found with ID {customer_id}"))
                return
        else:
            customers = Customer.objects.all()

        self.stdout.write(f"Found {customers.count()} customers to process.\n")

        for customer in customers:
            # FIX: robustness for User name display (kept your existing logic)
            user_name = f"Customer {customer.pk}" # Default
            if hasattr(customer, 'user'):
                u = customer.user
                user_name = getattr(u, 'name', getattr(u, 'username', getattr(u, 'email', str(u))))

            self.stdout.write(f"Processing: {user_name} (ID: {customer.pk})...")

            try:
                # --- STEP 1: UPDATE CUSTOMER PROFILE ---
                # This calculates and saves the new features (discount_sensitivity, etc.)
                self.stdout.write("  -> 1. Recalculating customer profile...")
                disc, price_elasticity, urgency = update_customer_profile(customer.pk)
                self.stdout.write(self.style.SUCCESS(
                    f"  -> Profile updated. Disc: {disc:.2f}, PriceElast: {price_elasticity:.2f}, Urgency: {urgency:.2f}"
                ))
                
                # --- STEP 2: GENERATE RECOMMENDATIONS ---
                # This uses the new features saved in Step 1 to generate predictions
                self.stdout.write("  -> 2. Generating recommendations...")
                recommendations = get_customer_recommendations(customer)

                if recommendations:
                    self.stdout.write(self.style.SUCCESS(f"  -> Success! Saved {len(recommendations)} recs."))
                    for rec in recommendations[:3]:
                        self.stdout.write(f"      * {rec['crop']}: {rec['purchase_prob']:.2f}")
                else:
                    self.stdout.write(self.style.WARNING("  -> No recommendations generated."))
                
                self.stdout.write("-" * 30)

            except Exception as e:
                # Print the full error but keep the loop going for other customers
                import traceback
                self.stdout.write(self.style.ERROR(f"  -> CRASH on Customer {customer.pk}: {str(e)}"))
                self.stdout.write(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS(f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] === COMPLETED SUCCESSFULLY ==="))
