"""Staff-only management dashboard."""
from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CategoryForm, OrderStatusForm, ProductForm
from .models import Category, Order, OrderItem, Product

line_total = ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())


@staff_member_required
def overview(request):
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    revenue = (OrderItem.objects.exclude(order__status=Order.Status.CANCELLED)
               .aggregate(v=Sum(line_total))["v"] or 0)
    revenue_30d = (OrderItem.objects.exclude(order__status=Order.Status.CANCELLED)
                   .filter(order__created__gte=month_ago)
                   .aggregate(v=Sum(line_total))["v"] or 0)

    stats = {
        "revenue": revenue,
        "revenue_30d": revenue_30d,
        "orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
        "products": Product.objects.count(),
        "customers": User.objects.filter(is_staff=False).count(),
    }
    low_stock = Product.objects.filter(stock__lte=5).order_by("stock")[:8]
    recent_orders = Order.objects.select_related("user")[:8]
    top_products = (OrderItem.objects.values("product_name")
                    .annotate(sold=Sum("quantity"), revenue=Sum(line_total))
                    .order_by("-sold")[:5])
    return render(request, "dashboard/overview.html", {
        "stats": stats, "low_stock": low_stock,
        "recent_orders": recent_orders, "top_products": top_products,
    })


@staff_member_required
def product_list(request):
    products = Product.objects.select_related("category").order_by("-created")
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    page = Paginator(products, 15).get_page(request.GET.get("page"))
    return render(request, "dashboard/product_list.html", {"page": page, "q": q})


@staff_member_required
def product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"“{product.name}” saved.")
        return redirect("dashboard:products")
    return render(request, "dashboard/product_form.html", {"form": form, "product": product})


@staff_member_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.info(request, f"“{name}” deleted.")
    return redirect("dashboard:products")


@staff_member_required
def categories(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added.")
        return redirect("dashboard:categories")
    cats = Category.objects.annotate(product_count=Count("products"))
    return render(request, "dashboard/categories.html", {"categories": cats, "form": form})


@staff_member_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.info(request, "Category deleted (its products were removed too).")
    return redirect("dashboard:categories")


@staff_member_required
def orders(request):
    qs = Order.objects.select_related("user").prefetch_related("items")
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "dashboard/orders.html", {
        "page": page, "status": status, "statuses": Order.Status.choices,
    })


@staff_member_required
@require_POST
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form = OrderStatusForm(request.POST, instance=order)
    if form.is_valid():
        form.save()
        messages.success(request, f"Order #{order.pk} marked {order.get_status_display().lower()}.")
    return redirect(request.POST.get("next") or "dashboard:orders")


@staff_member_required
def customers(request):
    users = (User.objects.filter(is_staff=False)
             .annotate(order_count=Count("orders"))
             .order_by("-date_joined"))
    page = Paginator(users, 15).get_page(request.GET.get("page"))
    return render(request, "dashboard/customers.html", {"page": page})


@staff_member_required
def inventory(request):
    products = Product.objects.select_related("category").order_by("stock")
    return render(request, "dashboard/inventory.html", {"products": products})
