from django import forms
from django.utils.translation import gettext_lazy as _

# A list of tuples representing the available product quantity choices.
# Each tuple contains an integer value and its corresponding string label.
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """
    A form class to validate the addition of a product to the cart.

    Attributes:
        quantity (forms.TypedChoiceField): A field to select the desired quantity.
        override (forms.BooleanField): A hidden field to indicate whether to override existing cart items.
    """

    # A field to select the desired quantity from the available choices.
    quantity = forms.TypedChoiceField(
        # The list of available quantity choices.
        choices=PRODUCT_QUANTITY_CHOICES,
        # Coerce the selected value to an integer for validation purposes.
        coerce=int,
        # The label to display next to the field in the form.
        label=_('Quantity')
    )

    # A hidden boolean field to indicate whether to override existing cart items.
    # This field is required=False by default, meaning it will not be displayed in the form.
    # However, when submitting the form with this field present, its value will override any existing cart items.
    override = forms.BooleanField(
        # Make the field optional (i.e., not required).
        required=False,
        # Initialize the field's value to False by default.
        initial=False,
        # Use a hidden input widget for this field so it won't be displayed in the form.
        widget=forms.HiddenInput
    )
