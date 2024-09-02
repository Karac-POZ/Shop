from .cart import Cart


def cart(request):
    """
    A view function to return the cart instance.

    Args:
        request (object): The current HTTP request.

    Returns:
        dict: A dictionary containing a single key-value pair, where the key is 'cart'
              and the value is an instance of the Cart class.
    """
    # Create a new instance of the Cart class with the given request object
    return {'cart': Cart(request)}
