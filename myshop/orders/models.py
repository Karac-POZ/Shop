from decimal import Decimal

from coupons.models import Coupon
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """
    Represents a customer's order.

    Attributes:
        first_name (str): The customer's first name.
        last_name (str): The customer's last name.
        email (str): The customer's email address.
        address (str): The customer's address.
        postal_code (str): The customer's postal code.
        city (str): The customer's city.
        created (datetime): The date and time the order was created.
        updated (datetime): The date and time the order was last updated.
        paid (bool): Whether the order has been paid in full.
        stripe_id (str): The ID of the Stripe payment associated with this order, if any.
        coupon (Coupon): The coupon used for this order, if any.
        discount (int): The percentage discount applied to this order.

    Methods:
        get_total_cost_before_discount(): Returns the total cost of the items in this order before any discounts are applied.
        get_discount(): Returns the amount of the discount applied to this order.
        get_total_cost(): Returns the total cost of the items in this order, taking into account any discounts.
        get_stripe_url(): Returns a URL for accessing the Stripe payment associated with this order.

    """
    first_name = models.CharField(_('first_name'), max_length=50)
    last_name = models.CharField(_('last_name'), max_length=50)
    email = models.EmailField(_('email'))
    address = models.CharField(_('address'), max_length=250)
    postal_code = models.CharField(_('postal_code'), max_length=20)
    city = models.CharField(_('city'), max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        Coupon,
        related_name='orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    discount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        """
        Metadata for the Order model.

        Attributes:
            ordering: The order in which orders are listed, with most recent first.
            indexes: Indexes used to improve query performance.

        """
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost_before_discount(self):
        """
        Returns the total cost of the items in this order before any discounts are applied.

        Returns:
            float: The total cost of the items in this order.

        """
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        """
        Returns the amount of the discount applied to this order.

        Returns:
            float: The amount of the discount applied to this order.

        """
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        """
        Returns the total cost of the items in this order, taking into account any discounts.

        Returns:
            float: The total cost of the items in this order.

        """
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_stripe_url(self):
        """
        Returns a URL for accessing the Stripe payment associated with this order.

        Returns:
            str: A URL for accessing the Stripe payment associated with this order.

        """
        if not self.stripe_id:
            # no payment associated
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # Stripe path for test payments
            path = '/test/'
        else:
            # Stripe path for real payments
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    """
    Represents an item in a customer's order.

    Attributes:
        order (Order): The order that this item is part of.
        product (Product): The product being ordered.
        quantity (int): The number of units of the product being ordered.

    Methods:
        get_cost(): Returns the cost of this item in the order.

    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'shop.Product',
        related_name='order_items',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """
        Returns the cost of this item in the order.

        Returns:
            float: The cost of this item in the order.

        """
        return self.price * self.quantity
