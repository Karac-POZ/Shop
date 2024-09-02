import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Order, OrderItem


def order_pdf(obj):
    """
    Generates a link to the admin_order_pdf view for the given order ID.

    Args:
        obj: The order object for which to generate the PDF invoice.

    Returns:
        A HTML link to the admin_order_pdf view.
    """
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF Invoice</a>')


order_pdf.short_description = 'Invoice'


def order_detail(obj):
    """
    Generates a link to the admin_order_detail view for the given order ID.

    Args:
        obj: The order object for which to generate the link.

    Returns:
        A HTML link to the admin_order_detail view.
    """
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View Order Details</a>')


def export_to_csv(modeladmin, request, queryset):
    """
    Exports the given orders to a CSV file.

    Args:
        modeladmin: The admin interface for the Order model.
        request: The HTTP request object.
        queryset: The list of order objects to export.

    Returns:
        A HttpResponse object containing the exported CSV data.
    """
    opts = modeladmin.model._meta
    content_disposition = (
        f'attachment; filename={opts.verbose_name}.csv'
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'


def order_payment(obj):
    """
    Generates a link to a Stripe payment page for the given order.

    Args:
        obj: The order object for which to generate the link.

    Returns:
        A HTML link to the Stripe payment page.
    """
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''


order_payment.short_description = 'Stripe payment'


class OrderItemInline(admin.TabularInline):
    """
    An inline admin form for OrderItem objects.
    """
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    The admin interface for the Order model.
    """
    list_display = [
        'id',
        'first_name',
        'last_name',
        'email',
        'address',
        'postal_code',
        'city',
        'paid',
        order_payment,
        'created',
        'updated',
        order_detail,
        order_pdf,
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
