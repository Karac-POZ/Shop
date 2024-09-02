from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    A form for creating new orders.

    Attributes:
        first_name (forms.CharField): The first name of the customer.
        last_name (forms.CharField): The last name of the customer.
        email (forms.EmailField): The email address of the customer.
        address (forms.CharField): The shipping address of the order.
        postal_code (forms.CharField): The postal code of the shipping address.
        city (forms.CharField): The city where the order is being shipped to.

    Methods:
        __init__(): Initializes the form with default values.
    """
    class Meta:
        """
        Metadata for the OrderCreateForm.

        Attributes:
            model (Order): The Django model associated with this form.
            fields (list[str]): A list of field names that should be included in the form.
        """
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'address',
            'postal_code',
            'city',
        ]
