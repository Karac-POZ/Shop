import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .tasks import payment_completed
from shop.models import Product
from shop.recommender import Recommender

# CSRF-отказано


@csrf_exempt
def stripe_webhook(request):
    """
    Обрабатывает вебхук Stripe.

    Проверяет подпись и payload, затем обрабатывает завершение сессии оплаты.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        HttpResponse: Возвращает ответ с статусом 200 или ошибками.
    """
    # Тело запроса
    payload = request.body
    # Подпись
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Конструирует событие вебхука Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Неправильный payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Неправильная подпись
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        # Сессия оплаты завершена
        session = event.data.object
        # Оплата выполнена и сессия типа 'payment'
        if (
            session.mode == 'payment'
            and session.payment_status == 'paid'
        ):
            try:
                # Получение заказа по client_reference_id
                order = Order.objects.get(
                    id=session.client_reference_id
                )
            except Order.DoesNotExist:
                # Заказ не найден
                return HttpResponse(status=404)
            # Помечает заказ как оплаченный
            order.paid = True
            # Сохранение идентификатора платежа Stripe
            order.stripe_id = session.payment_intent
            order.save()
            # Сохраняет купленные товары для рекомендаций
            product_ids = order.items.values_list('product_id')
            products = Product.objects.filter(id__in=product_ids)
            r = Recommender()
            r.products_bought(products)
            # Запуск асинхронной задачи
            payment_completed.delay(order.id)

    return HttpResponse(status=200)
