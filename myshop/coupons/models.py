from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    """
    A model for managing coupons with their respective details.

    Attributes:
        code (str): Unique identifier of the coupon.
        valid_from (datetime): Date and time from when the coupon is valid.
        valid_to (datetime): Date and time until the coupon is valid.
        discount (int): The percentage value of the discount offered by the coupon (0 to 100).
        active (bool): Whether the coupon is currently active or not.
    """
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage vaule (0 to 100)',
    )
    active = models.BooleanField()

    def __str__(self):
        """
        Returns a string representation of the coupon, which defaults to its code.

        Returns:
            str: The unique identifier of the coupon.
        """
        return self.code
