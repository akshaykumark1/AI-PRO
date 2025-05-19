from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category', 'rating', 'reviews')
    list_filter = ('category', 'rating')
    search_fields = ('title', 'description')
    ordering = ('-id',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'price')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__title')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'zip_code', 'country')
    search_fields = ('user__username', 'city', 'state', 'country')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('user__username', 'product__title')
