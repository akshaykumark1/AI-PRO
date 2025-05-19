from django.db import models
from django.utils import timezone
import datetime
from django.db.models.fields import CharField

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus
# from datetime import datetime, timedelta

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Product Model


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image2 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image3 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image4 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image5 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    reviews = models.IntegerField(default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.IntegerField(default=0)  # Percentage discount
    delivery_date = models.DateField(default=timezone.now)  # <-- Add default value here
    rating=models.FloatField(default=0)
    vector_data=models.TextField(null=True)

    def calculate_discount(self):
        if self.original_price and self.discounted_price:
            self.discount = int(((self.original_price - self.discounted_price) / self.original_price) * 100)
            self.save()


    def __str__(self):
        return self.title
class users(models.Model):
    name=models.ForeignKey(User,on_delete=models.CASCADE)
    vector_data=models.TextField(null=True)
    def __str__(self):
        return self.name.username
class SearchHistory(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(users, on_delete=models.CASCADE)

class ViewHistory(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(users,on_delete=models.CASCADE)        

# Cart Model
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def calculate_price(self):
        self.price = self.product.price * self.quantity
        self.save()

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"

# Order Model

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(_("Order ID"), max_length=40,null=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36,null=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128,null=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity})"



# adress model
class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=255)




# wishlist
class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist entries
        
    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.title}"


class reviews(models.Model):
    rating=models.IntegerField()
    description=models.TextField()
    uname=models.ForeignKey(users,on_delete=models.CASCADE)
    pname = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_reviews')
        