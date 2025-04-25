import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction
from .serializers import CartSerializer, CartItemSerializer
from .services import CartService
from .models import Cart, Product
from rest_framework_simplejwt.authentication import JWTAuthentication


from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class TestAPI(APIView):
    def get(self, request):
        return Response({"message": "ok"})


class CartViewSet(viewsets.GenericViewSet):

    """
    A viewset for managing the authenticated user's shopping cart.

    This viewset provides actions to:
    - Retrieve the current user's cart.
    - Add items to the cart.

    Permissions:
        - Requires the user to be authenticated.
    Throttling:
        - Uses the 'user' throttle scope to limit request rate.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    throttle_scope = 'user'

    def get_queryset(self):
        """
        Returns the queryset of the current user's cart with related product items prefetched.

        Returns:
            QuerySet: The user's cart with items and related product data.
        """
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')

    def get_cart(self):
        """
        Retrieves or creates the user's cart. If the cart is expired, it will be marked as expired
        using CartService.

        Returns:
            Cart: The current user's valid cart instance.
        """
        cart = self.get_queryset().first() or Cart.objects.create(user=self.request.user)
        if cart.is_expired:
            CartService.expire(cart)
        return cart

    def list(self, request, *args, **kwargs):
        """
        list the current user's shopping cart.

        HTTP GET /api/cart/

        Returns:
            Response: Serialized cart data.
        """
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request, *args, **kwargs):
        """
        Adds a product to the user's shopping cart.

        HTTP POST /api/cart/add/
        Body Parameters:
            - product_id (int): ID of the product to add.
            - quantity (int): Quantity of the product to add.

        Returns:
            Response: Updated cart data or an error response if the product does not exist
                      or if an invalid quantity is provided.
        """
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        qty = serializer.validated_data['quantity']

        try:
            cart = CartService.add_item(request.user, product_id, qty)
        except (Product.DoesNotExist, ValueError) as exc:
            logger.exception('Error adding to cart', extra={
                'user_id': request.user.id,
                'product_id': product_id,
                'quantity': qty
            })
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response = CartSerializer(cart).data
        return Response(response, status=status.HTTP_201_CREATED)