from rest_framework import serializers
from .models import Product, Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ('product_id', 'quantity')

    def validate_quantity(self, value):
        product_id = self.initial_data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Product not found')

        if product.inventory < value:
            raise serializers.ValidationError('Not enough inventory')
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'created_at', 'items', 'total_items')
        read_only_fields = ('id', 'user', 'created_at', 'total_items')

    @staticmethod
    def get_total_items(obj):
        return sum(item.quantity for item in obj.items.all())