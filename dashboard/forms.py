from django import forms
from store.models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'slug', 'description', 'price', 'stock', 'sizes', 'colors', 'is_featured', 'is_active', 'main_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'sizes': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'colors': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded text-accent-primary bg-[var(--glass-bg)] border-[var(--glass-border)] focus:ring-accent-primary'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded text-accent-primary bg-[var(--glass-bg)] border-[var(--glass-border)] focus:ring-accent-primary'}),
            'main_image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accent-primary file:text-white hover:file:bg-accent-secondary transition-all'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'slug', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-white placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary transition-all'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded text-accent-primary bg-[var(--glass-bg)] border-[var(--glass-border)] focus:ring-accent-primary'}),
        }
