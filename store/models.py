from django.db import models
from django.urls import reverse

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

    def get_representative_image(self):
        """Returns the image of the most recently added product in this category."""
        latest_product = self.products.exclude(main_image='').order_by('-created_at').first()
        if latest_product and latest_product.main_image:
            return latest_product.main_image.url
        return None

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    sizes = models.CharField(max_length=255, blank=True, help_text="Comma separated sizes (e.g., 39, 40, 41 or S, M, L)")
    colors = models.CharField(max_length=255, blank=True, help_text="Comma separated colors (e.g., Black, White, Red)")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def get_sizes_list(self):
        if self.sizes:
            return [s.strip() for s in self.sizes.split(',') if s.strip()]
        return []

    def get_colors_list(self):
        if self.colors:
            return [c.strip() for c in self.colors.split(',') if c.strip()]
        return []


from django.contrib.auth.models import User

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorited_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.rating}-star review for {self.product.title}"

    def __str__(self):
        return f"{self.user.username} favorited {self.product.title}"
