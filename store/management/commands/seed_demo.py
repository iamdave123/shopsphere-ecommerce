"""Populate the store with demo categories, products, users, reviews and orders.

Usage:  python manage.py seed_demo
Safe to re-run — it skips records that already exist.
"""
import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.models import Category, Order, OrderItem, Product, Review

CATEGORIES = [
    ("Electronics", "laptop", "Audio, computing and smart gadgets."),
    ("Home & Living", "house-heart", "Comfort and style for every room."),
    ("Apparel", "bag", "Wardrobe staples and seasonal picks."),
    ("Fitness", "bicycle", "Gear for training and recovery."),
    ("Beauty", "droplet", "Skincare and self-care essentials."),
    ("Books", "book", "Stories, skills and big ideas."),
]

PRODUCTS = [
    # name, category, price, compare_at, stock, featured, description
    ("Aurora Wireless Headphones", "Electronics", "89.00", "129.00", 24, True,
     "Over-ear wireless headphones with active noise cancelling, 40-hour battery life and plush memory-foam cushions."),
    ("Pulse Smartwatch S2", "Electronics", "149.00", None, 15, True,
     "Track workouts, sleep and notifications with a bright AMOLED display and 7-day battery."),
    ("Nimbus Mechanical Keyboard", "Electronics", "74.50", "94.00", 8, False,
     "Hot-swappable tactile switches, PBT keycaps and a satisfying typing feel for work or play."),
    ("Beacon Portable Speaker", "Electronics", "39.99", None, 40, False,
     "Pocket-sized Bluetooth speaker with surprisingly rich bass and 12 hours of playtime."),
    ("4K Action Camera Go", "Electronics", "119.00", "159.00", 6, False,
     "Waterproof to 10 m, with image stabilisation and a flip-up screen for vlogging."),
    ("Linen Throw Blanket", "Home & Living", "45.00", None, 30, True,
     "Stonewashed linen throw in warm ochre — breathable in summer, cosy in winter."),
    ("Ceramic Pour-Over Set", "Home & Living", "38.00", "48.00", 12, False,
     "Hand-glazed dripper and matching carafe for a slower, better morning coffee."),
    ("Scandi Oak Desk Lamp", "Home & Living", "59.00", None, 18, False,
     "Solid oak base with a linen shade and warm dimmable LED bulb included."),
    ("Aria Scented Candle Trio", "Home & Living", "29.00", None, 50, False,
     "Cedar, fig and sea-salt soy candles with 35-hour burn time each."),
    ("Everyday Canvas Tote", "Apparel", "24.00", None, 60, False,
     "Heavyweight organic cotton tote with an interior zip pocket. Carries your whole day."),
    ("Merino Crewneck Sweater", "Apparel", "78.00", "98.00", 14, True,
     "Ultra-soft extra-fine merino, knitted for year-round layering. Machine washable."),
    ("Trail Runner Jacket", "Apparel", "92.00", None, 9, False,
     "Wind-resistant, water-repellent shell that packs into its own pocket."),
    ("Classic Cap — Slate", "Apparel", "19.50", None, 35, False,
     "Six-panel brushed-cotton cap with an adjustable strap. Goes with everything."),
    ("Flexmat Pro Yoga Mat", "Fitness", "42.00", "55.00", 22, False,
     "6 mm cushioned, non-slip mat with alignment guides and a carry strap."),
    ("Adjustable Dumbbell 24 kg", "Fitness", "139.00", None, 5, False,
     "Fifteen weight settings in one compact dumbbell — a full rack in your living room."),
    ("Hydra Steel Bottle 1 L", "Fitness", "21.00", None, 80, False,
     "Double-wall insulated bottle keeps drinks cold 24 h or hot 12 h."),
    ("Recovery Foam Roller", "Fitness", "26.00", "34.00", 17, False,
     "High-density textured roller to release tight muscles after training."),
    ("Glow Vitamin-C Serum", "Beauty", "32.00", None, 28, True,
     "Brightening 15% vitamin C serum with hyaluronic acid for daily radiance."),
    ("Velvet Matte Lip Kit", "Beauty", "27.00", "36.00", 20, False,
     "Three long-wear matte shades with a nourishing balm core."),
    ("Botanic Hair Oil", "Beauty", "18.50", None, 33, False,
     "Lightweight argan and jojoba blend that tames frizz without the grease."),
    ("The Maker's Habit (Hardcover)", "Books", "22.00", None, 26, False,
     "A practical guide to building creative routines that actually stick."),
    ("Cooking by Season", "Books", "28.00", "35.00", 11, False,
     "120 market-driven recipes organised around what's fresh right now."),
    ("Atlas of Night Skies", "Books", "39.00", None, 7, False,
     "A beautifully illustrated tour of constellations, with star maps for every month."),
    ("Mindful Money", "Books", "17.00", None, 44, False,
     "Plain-spoken personal finance for people who hate spreadsheets."),
]

REVIEW_SNIPPETS = [
    (5, "Exceeded my expectations — quality feels well above the price."),
    (4, "Really solid. Shipping was quick and packaging was great."),
    (5, "Exactly as described. Would happily buy again."),
    (3, "Decent, though I expected slightly better finishing."),
    (4, "Good value. Been using it daily for two weeks with no issues."),
]


class Command(BaseCommand):
    help = "Seed the database with demo store data."

    def handle(self, *args, **options):
        random.seed(7)

        cats = {}
        for name, icon, desc in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"icon": icon, "description": desc})
            cats[name] = cat

        products = []
        for name, cat, price, compare, stock, featured, desc in PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults=dict(
                    category=cats[cat], price=Decimal(price),
                    compare_at_price=Decimal(compare) if compare else None,
                    stock=stock, featured=featured, description=desc,
                ),
            )
            products.append(product)
            if created:
                self.stdout.write(f"  + {name}")

        # Demo customers
        demo_users = []
        for username in ["amelia", "jordan", "priya"]:
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.com"},
            )
            if created:
                user.set_password("demo12345")
                user.save()
            demo_users.append(user)

        # Reviews
        if not Review.objects.exists():
            for product in random.sample(products, 12):
                for user in random.sample(demo_users, random.randint(1, 2)):
                    rating, comment = random.choice(REVIEW_SNIPPETS)
                    Review.objects.get_or_create(
                        product=product, user=user,
                        defaults={"rating": rating, "comment": comment},
                    )

        # A few historical orders so the dashboard has data
        if not Order.objects.exists():
            statuses = ["delivered", "delivered", "shipped", "processing", "pending"]
            for i, status in enumerate(statuses):
                user = demo_users[i % len(demo_users)]
                order = Order.objects.create(
                    user=user, full_name=user.username.title(), email=user.email,
                    address=f"{100 + i} Demo Street", city="Springfield",
                    postal_code="12345", status=status,
                )
                for product in random.sample(products, random.randint(1, 3)):
                    OrderItem.objects.create(
                        order=order, product=product, product_name=product.name,
                        price=product.price, quantity=random.randint(1, 2),
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Done. {Category.objects.count()} categories, {Product.objects.count()} products, "
            f"{Order.objects.count()} orders, {Review.objects.count()} reviews."
        ))
        self.stdout.write("Demo customer logins: amelia / jordan / priya — password: demo12345")
