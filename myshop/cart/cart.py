from decimal import Decimal

from coupons.models import Coupon
from django.conf import settings
from shop.models import Product


class Cart:
    """
    A class representing an e-commerce cart.

    Attributes:
        session (object): The current session.
        cart (dict): The cart items.
        coupon_id (int): The ID of the applied coupon.
    """

    def __init__(self, request):
        """
        Initializes the cart instance.

        Args:
            request (object): The current HTTP request.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        """
        Allows iteration over the cart items.

        Yields:
            dict: A dictionary representing a single cart item.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Returns the total quantity of items in the cart.

        Returns:
            int: The total quantity.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Adds a product to the cart or updates its quantity.

        Args:
            product (Product): The product to add.
            quantity (int, optional): The quantity of the product. Defaults to 1.
            override_quantity (bool, optional): Whether to override the existing quantity. Defaults to False.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Saves the cart session.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Removes a product from the cart.

        Args:
            product (Product): The product to remove.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Clears the entire cart.
        """
        del self.session['coupon_id']
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price(self):
        """
        Returns the total price of all items in the cart.

        Returns:
            Decimal: The total price.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    @property
    def coupon(self):
        """
        Returns the applied coupon or None if no coupon is applied.

        Returns:
            Coupon: The applied coupon or None.
        """
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        """
        Returns the discount amount based on the applied coupon.

        Returns:
            Decimal: The discount amount.
        """
        if self.coupon:
            return (
                self.coupon.discount / Decimal(100)
            ) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        """
        Returns the total price after applying any discounts.

        Returns:
            Decimal: The total price after discount.
        """
        return self.get_total_price() - self.get_discount()
