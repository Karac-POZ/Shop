from django.contrib import admin

# Import the Coupon model from models.py
from .models import Coupon


# A custom Django admin interface for the Coupon model.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Customizes the appearance and functionality of the Coupon model in the Django admin interface.

    Attributes:
        list_display (list): The fields to display on the admin change list page.
        list_filter (list): The fields to use as filters on the admin change list page.
        search_fields (list): The fields to search when searching for coupons on the admin change list page.
    """
    # Specify which fields to display on the admin change list page
    list_display = [
        'code',
        'valid_from',
        'valid_to',
        'discount',
        'active',
    ]

    # Specify which fields to use as filters on the admin change list page
    list_filter = ['active', 'valid_from', 'valid_to']

    # Specify which field(s) to search when searching for coupons on the admin change list page
    search_fields = ['code']
