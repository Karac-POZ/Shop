from django import forms
from django.utils.translation import gettext_lazy as _

# Represents a form for applying a coupon


class CouponApplyForm(forms.Form):
    """
    A form to apply a coupon.

    Attributes:
        code (CharField): The coupon code.
    """

    # Input field for the coupon code
    code = forms.CharField(label=_('Coupon'))
