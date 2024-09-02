import redis
from django.conf import settings
from .models import Product


# подключение к redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


class Recommender:
    """
    Класс для рекомендации продуктов на основе покупок пользователя.
    Attributes:
        None    
    Methods:
        get_product_key(id): Возвращает ключ для хранения данных о покупках продукта с заданным id.
        products_bought(products): Обновляет оценки продуктов, купленных вместе с заданными продуктами.
        suggest_products_for(products, max_results=6): Возвращает список рекомендуемых продуктов на основе покупок пользователя.
        clear_purchases(): Удаляет все данные о покупках из Redis.
    """

    def get_product_key(self, id):
        """
        Возвращает ключ для хранения данных о покупках продукта с заданным id.
        Args:
            id (int): Id продукта
        Returns:
            str: Ключ для хранения данных о покупках продукта
        """
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        """
        Обновляет оценки продуктов, купленных вместе с заданными продуктами.
        Args:
            products (list): Список продуктов
        Returns:
            None
        """
        products_ids = [p.id for p in products]
        for product_id in products_ids:
            for with_id in products_ids:
                # получить другие продукты, купленные вместе с каждым продуктом
                if product_id != with_id:
                    # оценка прироста для продукта, купленного вместе
                    r.zincrby(
                        self.get_product_key(product_id), 1, with_id
                    )

    def suggest_products_for(self, products, max_results=6):
        """
        Возвращает список рекомендуемых продуктов на основе покупок пользователя.
        Args:
            products (list): Список продуктов
        Returns:
            list: Список рекомендуемых продуктов
        """
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # только 1 продукт
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True
            )[:max_results]
        else:
            # генерация временного ключа
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            # несколько продуктов, объедините оценки всех продуктов
            # и сохраните полученный отсортированный набор во временном ключе
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # удалите id продуктов, для которых дана рекомендация
            r.zrem(tmp_key, *product_ids)
            # получить id продукта по его оценке, сортировка по убыванию
            suggestions = r.zrange(
                tmp_key, 0, -1, desc=True
            )[:max_results]
            # удалите временный ключ
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        # получать предлагаемые товары и сортировать их по порядку появления
        suggested_products = list(
            Product.objects.filter(id__in=suggested_products_ids)
        )
        suggested_products.sort(
            key=lambda x: suggested_products_ids.index(x.id)
        )
        return suggested_products

    def clear_purchases(self):
        """
        Удаляет все данные о покупках из Redis.
        Returns:
            None
        """
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
