from .cart import Cart
from .models import Category


def store_context(request):
    return {
        "cart": Cart(request),
        "nav_categories": Category.objects.all(),
    }
