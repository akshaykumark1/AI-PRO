from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','description', 'price', 'category','image1','image2','image3','image4','image5']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'city', 'state', 'zip_code', 'country']
