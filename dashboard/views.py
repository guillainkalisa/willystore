from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from store.models import Product, Category, ProductImage
from orders.models import Order
from .forms import ProductForm, CategoryForm
from .ai_utils import analyze_product_image_with_ai

@staff_member_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    revenue = sum(order.get_total_cost() for order in Order.objects.filter(paid=True))
    total_products = Product.objects.count()
    recent_orders = Order.objects.order_by('-created')[:5]
    
    return render(request, 'dashboard/index.html', {
        'total_orders': total_orders,
        'revenue': revenue,
        'total_products': total_products,
        'recent_orders': recent_orders,
    })

@staff_member_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    form = ProductForm()
    return render(request, 'dashboard/products.html', {'products': products, 'form': form})

@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            for image in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=product, image=image)
            messages.success(request, 'Product created successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form})

@staff_member_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            for image in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=product, image=image)
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product})

@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


@staff_member_required
def order_list(request):
    orders = Order.objects.prefetch_related('items__product').all().order_by('-created')
    return render(request, 'dashboard/orders.html', {'orders': orders})

@staff_member_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'paid':
            order.paid = True
        elif status == 'pending':
            order.paid = False
        order.save()
        messages.success(request, f'Order status updated to {status}.')
    return redirect('dashboard:order_list')


@staff_member_required
def category_list(request):
    categories = Category.objects.all().order_by('title')
    form = CategoryForm()
    return render(request, 'dashboard/categories.html', {'categories': categories, 'form': form})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {'form': form})

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'category': category})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/category_confirm_delete.html', {'category': category})

@staff_member_required
@require_POST
def analyze_image(request):
    """Asynchronous endpoint to auto-generate product details using Gemini AI Vision."""
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)
        
    image_file = request.FILES['image']
    
    # Process through Gemini AI
    ai_data = analyze_product_image_with_ai(image_file)
    
    # Try to fuzzy match the AI's category suggestion to an actual SQL database Category
    suggested_cat = ai_data.get('category_suggestion', '')
    category_id = None
    if suggested_cat:
        # Simple case-insensitive match
        match = Category.objects.filter(title__icontains=suggested_cat).first()
        if match:
            category_id = match.id
            
    ai_data['category_id'] = category_id
    
    return JsonResponse(ai_data)


@staff_member_required
@require_POST
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, pk=image_id)
    image.delete()
    return JsonResponse({'status': 'success'})
