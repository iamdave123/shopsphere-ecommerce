from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, RegisterForm, ReviewForm
from .models import Category, Order, OrderItem, Product


def home(request):
    featured = Product.objects.filter(is_active=True, featured=True)[:4]
    new_arrivals = Product.objects.filter(is_active=True)[:8]
    deals = [p for p in Product.objects.filter(is_active=True, compare_at_price__isnull=False) if p.on_sale][:4]
    return render(request, "store/home.html", {
        "featured": featured, "new_arrivals": new_arrivals, "deals": deals,
        "categories": Category.objects.all(),
    })


def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    sort = request.GET.get("sort", "new")
    sort_map = {"new": "-created", "price_asc": "price", "price_desc": "-price", "name": "name"}
    products = products.order_by(sort_map.get(sort, "-created"))

    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "store/product_list.html", {
        "category": category, "page": page, "q": q, "sort": sort,
        "total": paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    review_form = ReviewForm()
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()

    if request.method == "POST" and request.user.is_authenticated:
        review_form = ReviewForm(request.POST, instance=user_review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks — your review was saved.")
            return redirect(product.get_absolute_url())

    return render(request, "store/product_detail.html", {
        "product": product, "related": related,
        "review_form": review_form, "user_review": user_review,
    })


# ---------- Cart ----------

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = max(1, int(request.POST.get("quantity", 1)))
    if not product.in_stock:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(product.get_absolute_url())
    cart.add(product, quantity=quantity, override=request.POST.get("override") == "1")
    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("next") or "store:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        cart.remove(product)
    else:
        cart.add(product, quantity=quantity, override=True)
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} removed from your cart.")
    return redirect("store:cart_detail")


def cart_detail(request):
    return render(request, "store/cart.html")


# ---------- Checkout & orders ----------

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("store:product_list")

    initial = {"full_name": request.user.get_full_name(), "email": request.user.email}
    form = CheckoutForm(initial=initial)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()
                for item in cart:
                    product = item["product"]
                    qty = min(item["quantity"], product.stock)
                    if qty == 0:
                        continue
                    OrderItem.objects.create(
                        order=order, product=product, product_name=product.name,
                        price=item["price"], quantity=qty,
                    )
                    product.stock -= qty
                    product.save(update_fields=["stock"])
            cart.clear()
            messages.success(request, f"Order #{order.pk} placed — thank you!")
            return redirect("store:order_success", order_id=order.pk)

    return render(request, "store/checkout.html", {"form": form})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    qs = Order.objects.prefetch_related("items__product")
    if request.user.is_staff:
        order = get_object_or_404(qs, pk=order_id)
    else:
        order = get_object_or_404(qs, pk=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})


# ---------- Auth ----------

def register(request):
    if request.user.is_authenticated:
        return redirect("store:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, "Account created — please sign in to continue.")
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})