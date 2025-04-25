from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Product, Cart

User = get_user_model()

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', 'u@e.com', 'pass')
        self.client.force_authenticate(user=self.user)

        self.prod = Product.objects.create(name='P', inventory=5)

    def test_add_and_view(self):
        # Use custom cart-add endpoint
        add_url = reverse('cart-add')  # <-- fix here
        response = self.client.post(add_url,
                                    {'product_id': self.prod.id, 'quantity': 3},
                                    format='json')
        self.assertEqual(response.status_code, 201)

        self.prod.refresh_from_db()
        self.assertEqual(self.prod.inventory, 2)

        # /cart/ returns the current cart
        detail_url = reverse('cart-list')  # <-- list returns the current cart
        res2 = self.client.get(detail_url)
        self.assertEqual(res2.status_code, 200)

        items = res2.data.get('items', [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['quantity'], 3)

    def test_over_inventory(self):
        add_url = reverse('cart-add')  # <-- fix here
        res = self.client.post(add_url,
                               {'product_id': self.prod.id, 'quantity': 6},
                               format='json')
        self.assertEqual(res.status_code, 400)

    def test_expiration(self):
        add_url = reverse('cart-add')  # <-- fix here
        response = self.client.post(add_url,
                                    {'product_id': self.prod.id, 'quantity': 2},
                                    format='json')
        self.assertEqual(response.status_code, 201)

        cart = Cart.objects.get(user=self.user)
        cart.created_at -= timezone.timedelta(minutes=31)
        cart.save()

        detail_url = reverse('cart-list')  # <-- this triggers expiration
        self.client.get(detail_url)

        self.prod.refresh_from_db()
        self.assertEqual(self.prod.inventory, 5)
