from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json # Added for JSON parsing
from .models import Category, Product, Favorite, Review # Added Review

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    # For homepage, we might want featured products
    featured_products = products.filter(is_featured=True)[:8]

    # Extract query parameters
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Filtering by Search Query
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # Filtering by Price Range
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=int(max_price))

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    current_filters = {
        'q': query,
        'sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }

    favorite_product_ids = []
    if request.user.is_authenticated:
        favorite_product_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
        'current_filters': current_filters,
        'favorite_product_ids': favorite_product_ids
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    reviews = product.reviews.all()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'is_favorite': is_favorite,
        'reviews': reviews
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@require_POST
def add_review(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please sign in to leave a review.'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')
    
    if rating and comment:
        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        return JsonResponse({'status': 'success', 'message': 'Review submitted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Please provide a rating and a comment.'}, status=400)

@login_required
def toggle_favorite(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        favorite = Favorite.objects.filter(user=request.user, product=product).first()
        if favorite:
            favorite.delete()
            return JsonResponse({'status': 'removed'})
        else:
            Favorite.objects.create(user=request.user, product=product)
            return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def favorites(request):
    favorite_items = Favorite.objects.filter(user=request.user).select_related('product')
    products = [f.product for f in favorite_items]
    return render(request, 'store/favorites.html', {'products': products})
