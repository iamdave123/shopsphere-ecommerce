# ShopSphere — Django E-Commerce Web Application

A full-stack e-commerce platform built with **Django 5, HTML, CSS, JavaScript, Bootstrap 5 and SQLite**. Customers can browse products, search and filter, manage a shopping cart, place orders and track them through a status timeline. Staff manage products, categories, inventory, customers and orders through a secure dashboard.

## Quick start

```bash
# 1. Install dependencies (a virtualenv is recommended)
pip install -r requirements.txt

# 2. Set up the database
python manage.py migrate

# 3. (Optional) Load demo data — 6 categories, 24 products, sample orders & reviews
python manage.py seed_demo

# 4. Create your admin account
python manage.py createsuperuser

# 5. Run it
python manage.py runserver
```

and sign in

.....

## Features

**Storefront**
- Home page with hero, category tiles, featured products, deals and new arrivals
- Product catalog with category filtering, keyword search, sorting and pagination
- Product detail pages with sale badges, stock indicators, ratings and customer reviews
- Session-based shopping cart (works for guests) with quantity steppers, capped at available stock
- Checkout with shipping form and demo payment selection; stock is decremented atomically
- Order tracking: "My orders" list plus a per-order status timeline (pending → processing → shipped → delivered)
- User registration, login/logout

**Staff dashboard** (`/dashboard/`, protected by `staff_member_required`)
- Overview: all-time & 30-day revenue, order/customer counts, best sellers, low-stock alerts, recent orders
- Product management: create, edit, delete, image upload, featured/visibility flags, search
- Category management with product counts
- Inventory view sorted by stock level with out-of-stock / low-stock highlighting
- Order management with one-click status updates and filtering
- Customer list with order counts
- Django admin also available at `/admin/` for power users

## Project layout

```
ecommerce/            Project settings & root URLs
store/
  models.py           Category, Product, Review, Order, OrderItem
  views.py            Storefront views (catalog, cart, checkout, orders, auth)
  dashboard_views.py  Staff dashboard views
  cart.py             Session-based Cart class
  forms.py            Checkout, registration, review & dashboard forms
  management/commands/seed_demo.py   Demo data loader
templates/            base.html + store/, dashboard/, registration/
static/css|js         Custom theme (teal & saffron) and cart/quantity JS
media/products/       Uploaded product images
db.sqlite3            SQLite database (pre-seeded in this archive)
```

## Notes for production

This project ships in development mode. Before deploying: set `DEBUG = False`, move `SECRET_KEY` to an environment variable, restrict `ALLOWED_HOSTS`, serve static/media files properly (e.g. WhiteNoise + object storage), and switch to a production database if traffic warrants it.
