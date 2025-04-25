from django.utils import timezone
from django.db import transaction
from django.db.models import F
from .models import Cart, CartItem, Product

class CartService:
    @staticmethod
    @transaction.atomic
    def add_item(user, product_id, qty):
        # Lock the product row
        product = Product.objects.select_for_update().get(id=product_id)
        if product.inventory < qty:
            raise ValueError('Insufficient inventory')

        cart, created = Cart.objects.get_or_create(user=user)
        if not created and cart.is_expired:
            CartService.expire(cart)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': qty}
        )
        if not created:
            item.quantity = F('quantity') + qty
            item.save()

        # atomic inventory decrement
        Product.objects.filter(id=product_id).update(inventory=F('inventory') - qty)
        return cart

    @staticmethod
    def expire(cart):
        # Restore inventory and clear items
        for item in cart.items.all():
            Product.objects.filter(id=item.product_id).update(
                inventory=F('inventory') + item.quantity
            )
        cart.items.all().delete()

        cart.created_at = timezone.now()
        cart.save()