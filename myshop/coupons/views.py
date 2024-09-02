from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from .models import Coupon


# Apply coupon to the user's cart
@require_POST
def coupon_apply(request):
    """
    Handles the application of a coupon code to the user's shopping cart.
    Checks if the coupon is valid and active, then applies it by storing its ID in the session.
    If the coupon does not exist or is invalid, stores `None` in the session instead.
    Redirects the user to their cart details page after applying the coupon.

    Args:
        request: The HTTP request object.
    Returns:
        A redirect response to the cart details page.
    """
    now = timezone.now()
    # Create a form instance with the provided POST data
    form = CouponApplyForm(request.POST)
    # Check if the form is valid
    if form.is_valid():
        # Get the coupon code from the cleaned form data
        code = form.cleaned_data['code']
        try:
            # Attempt to retrieve a coupon object with the given code
            coupon = Coupon.objects.get(
                # Use case-insensitive matching for the coupon code
                code__iexact=code,
                # Ensure the coupon is valid on the current date and time
                valid_from__lte=now,
                valid_to__gte=now,
                # Only consider active coupons
                active=True,
            )
            # Store the ID of the applied coupon in the user's session
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            # If the coupon does not exist or is invalid, store `None` in the session instead
            request.session['coupon_id'] = None
    return redirect('cart:cart_detail')
