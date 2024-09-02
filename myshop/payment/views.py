from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
import stripe
from django.conf import settings
from django.urls import reverse
from orders.models import Order


# Создаем экземпляр Stripe
# Публичный ключ для подключения к API Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION  # Версия API Stripe


def payment_process(request):
    """
    Обрабатывает процесс оплаты заказа.

    Если метод запроса POST и форма валидна, создаёт сессию оплаты Stripe,
    добавляет элементы заказа в сессию, создаёт купон для скидки (если есть),
    перенаправляет на форму оплаты Stripe.
    В противном случае отображает шаблон 'payment/process.html'.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        HttpResponse: Возвращает ответ с либо отображением шаблона,
            либо перенаправлением на форму оплаты Stripe.
    """
    order_id = request.session.get('order_id')  # Получает ID заказа из сессии
    # Ищет заказ по ID и обрабатывает ошибку
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # URL-адрес для перенаправления после успешной оплаты
        success_url = reverse('payment:completed')
        # URL-адрес для перенаправления при отмене оплаты
        cancel_url = reverse('payment:canceled')

        # Данные сессии оформления заказа Stripe
        session_data = {
            'mode': 'payment',  # Режим оплаты
            'client_reference_id': order.id,  # ID клиента в сессии
            'success_url': success_url,  # URL-адрес для перенаправления после успешной оплаты
            'cancel_url': cancel_url,  # URL-адрес для перенаправления при отмене оплаты
            'line_items': []  # Список элементов заказа
        }
        # Добавление элементов заказа в сессию оформления заказа Stripe
        for item in order.items.all():
            session_data['line_items'].append(
                {
                    'price_data': {  # Данные о цене
                        # Цена без десятичной точки
                        'unit_amount': int(item.price * Decimal('100')),
                        'currency': 'usd',  # Валюта
                        'product_data': {  # Данные о товаре
                            'name': item.product.name,  # Название товара
                        },
                    },
                    'quantity': item.quantity,  # Количество товаров
                }
            )
        # Создание купона для скидки (если есть)
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code,
                percent_off=order.discount,
                duration='once'
            )
            session_data['discounts'] = [{'coupon': stripe_coupon.id}]
        # Создание сессии оплаты Stripe
        session = stripe.checkout.Session.create(**session_data)
        # Перенаправляет на форму оплаты Stripe
        return redirect(session.url, code=303)
    else:
        # Отображает шаблон 'payment/process.html' при GET-запросе
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    """
    Обрабатывает окончание процесса оплаты.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        HttpResponse: Возвращает ответ с отображением шаблона.
    """
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    """
    Обрабатывает отмену процесса оплаты.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        HttpResponse: Возвращает ответ с отображением шаблона.
    """
    return render(request, 'payment/canceled.html')
