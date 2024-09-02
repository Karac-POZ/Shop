from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    """
    Модель для категорий.
    Args:
        None
    Returns:
        None
    """
    # Поля для перевода и хранения информации о категории
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200, unique=True),
    )

    class Meta:
        """
        Подкласс с мета-информацией.
        Args:
            None
        Returns:
            None
        """
        # Имя для отображения в админке
        verbose_name = 'category'
        # Имя для отображения в админке во множественном числе
        verbose_name_plural = 'categories'

    def __str__(self):
        """
        Строковое представление объекта.
        Args:
            None
        Returns:
            str: Имя категории
        """
        return self.name

    def get_absolute_url(self):
        """
        Абсолютный URL для категории.
        Args:
            None
        Returns:
            str: URL для списка товаров по категории
        """
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(TranslatableModel):
    """
    Модель для продуктов.
    Args:
        None
    Returns:
        None
    """
    # Поля для перевода и хранения информации о продукте
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200),
        description=models.TextField(blank=True),
    )
    # Ссылка на категорию, в которой находится продукт
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )
    # Путь для загрузки изображения продукта
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        blank=True
    )
    # Цена продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Флаг доступности продукта
    available = models.BooleanField(default=True)
    # Дата создания продукта
    created = models.DateTimeField(auto_now_add=True)
    # Дата последнего обновления продукта
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Подкласс с мета-информацией.
        Args:
            None
        Returns:
            None
        """
        # Индексация поля создания для быстрого поиска
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        """
        Строковое представление объекта.
        Args:
            None
        Returns:
            str: Имя продукта
        """
        return self.name

    def get_absolute_url(self):
        """
        Абсолютный URL для продукта.
        Args:
            None
        Returns:
            str: URL для страницы продукта
        """
        return reverse('shop:product_detail', args=[self.id, self.slug])
