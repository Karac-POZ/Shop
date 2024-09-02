from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from .recommender import Recommender


def product_list(request, category_slug=None):
    """
    Возвращает список продуктов по заданному слагу категории или всех доступных продуктов.
    Args:
        request (object): Объект запроса
    Keyword Args:
        category_slug (str, optional): Слаг категории. Defaults to None.
    Returns:
        render: Рендеринг шаблона shop/product/list.html с данными о продуктах и категориях.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        # Получить категорию по слагу
        language = request.LANGUAGE_CODE
        category = get_object_or_404(
            Category,
            translations__language_code=language,
            translations__slug=category_slug
        )

        # Фильтровать продукты по выбранной категории
        products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'products': products,
        }
    )


def product_detail(request, id, slug):
    """
    Возвращает страницу детальной информации о продукте.
    Args:
        request (object): Объект запроса
    Keyword Args:
        id (int): Id продукта
        slug (str): Слаг продукта
    Returns:
        render: Рендеринг шаблона shop/product/detail.html с данными о продукте и рекомендованными товарами.
    """
    language = request.LANGUAGE_CODE
    product = get_object_or_404(
        Product,
        id=id,
        translations__language_code=language,
        translations__slug=slug,
        available=True
    )

    # Форма добавления продукта в корзину
    cart_product_form = CartAddProductForm()

    # Рекомендации продуктов
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    return render(
        request,
        'shop/product/detail.html',
        {
            'product': product,
            'cart_product_form': cart_product_form,
            'recommended_products': recommended_products,
        },
    )
