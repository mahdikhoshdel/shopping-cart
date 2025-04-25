from django.conf import settings
from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    inventory = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products"
        verbose_name = "Product"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=1)

    def __str__(self):
        return f"Cart({self.user})"

    class Meta:
        verbose_name_plural = "Cart"
        verbose_name = "Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name_plural = "CartItems"
        verbose_name = "CartItem"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"