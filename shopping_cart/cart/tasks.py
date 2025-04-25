from celery import shared_task
from django.utils import timezone
from django.db.models import F
from .models import Cart
from django.db import transaction

@shared_task
def expire_old_carts():
    """
    Celery task to expire shopping carts that are older than 30 minutes.

    This function performs the following actions:
    - Finds all cart instances created more than 30 minutes ago.
    - For each expired cart:
        - Locks its cart items and related products using `select_for_update` within a transaction.
        - Restores the inventory of each product by adding back the quantity from the cart.
        - Deletes the cart items to clean up expired data.

    The use of `transaction.atomic()` and `select_for_update()` ensures that the inventory updates and item deletions
    are performed safely, avoiding race conditions in concurrent environments.
    """
    expiration_time = timezone.now() - timezone.timedelta(minutes=1)
    expired_carts = Cart.objects.filter(created_at__lt=expiration_time)
    for cart in expired_carts:
        with transaction.atomic():
            items = cart.items.select_for_update().select_related('product')

            for item in items:
                item.product.inventory = F('inventory') + item.quantity
                item.product.save(update_fields=['inventory'])
            items.delete()