from django.urls import path
from . import dashboard_views as v

app_name = "dashboard"

urlpatterns = [
    path("", v.overview, name="overview"),
    path("products/", v.product_list, name="products"),
    path("products/new/", v.product_form, name="product_new"),
    path("products/<int:pk>/edit/", v.product_form, name="product_edit"),
    path("products/<int:pk>/delete/", v.product_delete, name="product_delete"),
    path("categories/", v.categories, name="categories"),
    path("categories/<int:pk>/delete/", v.category_delete, name="category_delete"),
    path("orders/", v.orders, name="orders"),
    path("orders/<int:pk>/status/", v.order_status, name="order_status"),
    path("customers/", v.customers, name="customers"),
    path("inventory/", v.inventory, name="inventory"),
]
