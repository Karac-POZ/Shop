from django.contrib import admin
from django.http import HttpRequest
from .models import Category, Product
from parler.admin import TranslatableAdmin


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    """
    Админ-панель для категорий.

    Добавляет поля 'name' и 'slug' в список для отображения.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        None
    """

    list_display = ['name', 'slug']

    # Поля для автозаполнения слага из имени
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    """
    Админ-панель для продуктов.

    Добавляет поля 'name', 'slug', 'price', 'available',
    'created', и 'updated' в список для отображения.

    Args:
        request (HttpRequest): Текущий HTTP-запрос.

    Returns:
        None
    """

    list_display = [
        'name',
        'slug',
        'price',
        'available',
        'created',
        'updated'
    ]
    # Фильтры для списка продуктов
    list_filter = ['available', 'created', 'updated']
    # Поля которые доступны к редактированию в списке
    list_editable = ['price', 'available']

    # Поля для автозаполнения слага из имени
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
