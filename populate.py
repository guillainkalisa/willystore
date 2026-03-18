import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "willystore.settings")
django.setup()

from store.models import Category, Product

# Create Categories
categories = ['Men', 'Women', 'Kids', 'Shoes', 'Accessories']
for cat in categories:
    Category.objects.get_or_create(title=cat, slug=cat.lower())

# Get Categories
men = Category.objects.get(slug='men')
shoes = Category.objects.get(slug='shoes')

# Create Products
Product.objects.get_or_create(
    category=shoes,
    title='Kigali Premium Sneakers',
    slug='kigali-premium-sneakers',
    description='The best sneakers for walking the hills of Kigali. Comfort meets premium style.',
    price=120.00,
    stock=10,
    is_featured=True
)

Product.objects.get_or_create(
    category=men,
    title='Classic Evening Jacket',
    slug='classic-evening-jacket',
    description='A highly stylish jacket perfect for Kigali evenings.',
    price=250.00,
    stock=5,
    is_featured=True
)

print("Sample data populated successfully.")
