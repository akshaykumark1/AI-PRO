# myapp/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .forms import *
import razorpay
import json
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import pandas as pd
from django.db.models import Case, When
from .read_content import *

import numpy as np
from .vectorize import vectorize_product_with_reviews,vectorize_user_with_search,pd

def signin(request):
    if request.user.is_authenticated:
        print(request.user)
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if  user.is_superuser:
                return redirect('admin')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'signin.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        
        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            # Create user account
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            dt= users.objects.create(name=user)
            dt.save()
            
            # Initialize user data for vectorization
            user_data = [{
                "user_id": user.id,
                "product": "",  
                "search": "",   
            }]
            
            # Create dataframe and generate vector
            df = pd.DataFrame(user_data)
            user_vectors = vectorize_user_with_search(df)
            
            # Ensure we have a valid vector before saving
            dt.vector_data = json.dumps(user_vectors[0].tolist())
            dt.save()
            print(f"User profile created successfully: {dt}")
            messages.success(request, "Account created successfully with user vector profile!")
        return redirect('signin')
    
    return render(request, "signup.html")


def userlogout(request):
    request.session.flush()
    return render(request, 'base.html')









def orders(request):
    return render(request, 'user/orders.html')  
def help(request):
    return render(request, 'user/help.html') 



def product_buy(request):
    products = Product.objects.all()

    return render(request, 'user/product_buy.html', {'products': products})

def wheretobuy(request):
    return render(request,'user/wheretobuy.html')

def buy_now(request,product_id):    
    return render(request,'buy_now.html')



##########################admin#####################



def orders(request):
    return render(request, 'user/orders.html')  
def help(request):
    return render(request, 'user/help.html') 



def product_buy(request):
    products = Product.objects.all()

    return render(request, 'user/product_buy.html', {'products': products})

def wheretobuy(request):
    return render(request,'user/wheretobuy.html')

def buy_now(request,product_id):    
    return render(request,'buy_now.html')

def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('address')  # Change to your address list view name
    else:
        form = AddressForm(instance=address)
    return render(request, 'user/edit_address.html', {'form': form})


##########################admin#####################

def order(request):
    orders = Order.objects.all()
    return render(request, 'admin/orders.html', {'orders': orders})


def address(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'user/address.html', {'addresses': addresses})



def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    address.delete()
    return redirect('address') 




def getuser(request):
    return request.session.get('username')

def filter_price(data, price):
    price2 = []
    for i in data:
        for j in price:
            if i.pk == j.product.pk:
                price2.append(j)
                break
    return price2


def types(request):
    type2 = []
    for i in Product.objects.all():
        if i.category and i.category.name not in type2:
            type2.append(i.category.name)
    return type2

model = SentenceTransformer('all-MiniLM-L6-v2')

def search_func(request):
    if request.method == 'POST':
        inp = request.POST.get('searched', '').strip()

        if not inp:
            return redirect('home')

        auth_user = None
        users_data = None

        if 'username' in request.session:
            try:
                auth_user = User.objects.get(username=request.session['username'])
                users_data = users.objects.get(name=auth_user)
            except (User.DoesNotExist, users.DoesNotExist):
                pass

        if auth_user and users_data:
            # Save search history
            SearchHistory.objects.create(query=inp, user=users_data)

            # Get search history
            user_search_queries = [search.query for search in SearchHistory.objects.filter(user=users_data)]

            # Collect previously viewed or purchased product titles
            user_products = [
                view.product.title for view in ViewHistory.objects.filter(user=users_data)
            ] + [
                order.product.title for order in Order.objects.filter(user=auth_user)
            ]

            # Prepare data for vectorization
            user_data = [{
                'user_id': auth_user.id,
                'product': ','.join(user_products),
                'search': ','.join(user_search_queries),
            }]
            df = pd.DataFrame(user_data)

            # Vectorize and save
            user_vectors = vectorize_user_with_search(df)
            users_data.vector_data = json.dumps(user_vectors[0].tolist())
            users_data.save()

        # Search products using icontains
        products = Product.objects.filter(
            Q(title__icontains=inp) | Q(description__icontains=inp) | Q(category__name__icontains=inp)
        ).distinct()

        return render(request, 'user/search.html', {
            'category': types(request),
            'user': getuser(request),
            'query': inp,
            'products': products
        })

    return redirect('home')





# def home(request):
#     data = Product.objects.all()
#     products = []

#     product_ids = [pro.pk for pro in data]
#     product_vectors = [json.loads(pro.vector_data) for pro in data]
#     product_vectors = np.array(product_vectors)
#     product_vectors = torch.tensor(product_vectors)

#     if request.user.is_authenticated:
#         try:
#             print("print", request.user.username)
#             user = User.objects.get(username=request.user.username)
#             user = users.objects.get(name=user)  # Ensure 'users' is correct
#             user_vector = json.loads(user.vector_data)
#             recommend_products = recommend_product(user_vector, product_vectors, product_ids, top_n=12)
#             print(recommend_products)
#             products = [i[0] for i in recommend_products]
#             preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(products)])
#             products = Product.objects.filter(pk__in=products).order_by(preserved_order)
#             print(products)
#         except (User.DoesNotExist, users.DoesNotExist):
#             products = Product.objects.all()[:12]  # Fallback
#     else:
#         products = Product.objects.all()[:12]  # Fallback for unauthenticated users

#     data2 = Product.objects.all()[:4]
#     data3 = Product.objects.all().order_by('-id')[:3]

#     return render(request, 'base.html', {
#         'data': data2,
#         'products': products,
#         'user': request.user,
#         'type': types(request)
#     })


def home(request):
    data = Product.objects.all()
    products = []

    product_ids = [pro.pk for pro in data]
    product_vectors = [json.loads(pro.vector_data) for pro in data if pro.vector_data]
    if not product_vectors:
        print("No valid product vectors found, falling back to default")
        products = Product.objects.all()[:12]
    else:
        product_vectors = np.array(product_vectors)
        product_vectors = torch.tensor(product_vectors)

        if request.user.is_authenticated:
            try:
                print("Authenticated user:", request.user.username)
                user = User.objects.get(username=request.user.username)
                user_profile = users.objects.get(name=user)
                user_vector = json.loads(user_profile.vector_data)
                recommend_products = recommend_product(user_vector, product_vectors, product_ids, top_n=12)
                print("Recommended products:", recommend_products)
                products = [i[0] for i in recommend_products]
                preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(products)])
                products = Product.objects.filter(pk__in=products).order_by(preserved_order)
                print("Products to render:", [p.title for p in products])
            except (User.DoesNotExist, users.DoesNotExist) as e:
                print("Error fetching user:", e)
                products = Product.objects.all()[:12]
        else:
            print("Unauthenticated user, showing default products")
            products = Product.objects.all()[:12]

    data2 = Product.objects.all()[:4]
    data3 = Product.objects.all().order_by('-id')[:3]

    return render(request, 'base.html', {
        'data': data2,
        'products': products,
        'user': request.user,
        'type': types(request),
    })


def admin(request):
    context = {
        'products': Product.objects.all().order_by('-id'),
        'orders': Order.objects.all().order_by('-id'),
    }
    return render(request, 'admin/admin.html', context)


def add_product(request):
    if request.method == "POST":
        categories = Category.objects.all()

        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        original_price = request.POST.get("original_price")
        discount = request.POST.get("discount", 0)
        category_id = request.POST.get("category")

        image1 = request.FILES.get("image1")
        image2 = request.FILES.get("image2")
        image3 = request.FILES.get("image3")
        image4 = request.FILES.get("image4")
        image5 = request.FILES.get("image5")


        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                messages.error(request, "Selected category does not exist.")
                return render(request, 'admin/add_product.html', {'categories': categories})

        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            original_price=original_price,
            discount=discount,
            category=category,
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4,
            image5=image5,
        )
        product.save()
        # Create vector data (optional)
        df = pd.DataFrame([{
            "id": product.id,
            "title": title,
            "rating": 0,
            "category": category.name if category else "",
            "description": description,
            "reviews": '',
        }])
        product_vector = vectorize_product_with_reviews(df)
        product.vector_data = json.dumps(product_vector[0].tolist())
        product.save()
        messages.success(request, "Product added successfully!")
        print(product)

    # Fallback in case of GET or error
    categories = Category.objects.all()
    print("printed")
    return render(request, 'admin/add_product.html', {'categories': categories})



def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    # Prepare the image fields list for rendering
    image_fields = [
        ('image1', product.image1),
        ('image2', product.image2),
        ('image3', product.image3),
        ('image4', product.image4),
        ('image5', product.image5),
    ]

    if request.method == 'POST':
        # Process form data
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.category_id = request.POST.get('category')
        product.original_price = request.POST.get('original_price')
        product.discount = request.POST.get('discount')
        product.delivery_date = request.POST.get('delivery_date')

        # Update image fields if new files are uploaded
        for i in range(1, 6):
            image_field = f'image{i}'
            uploaded_image = request.FILES.get(image_field)
            if uploaded_image:
                setattr(product, image_field, uploaded_image)

        product.save()  # Save the updated product

        return redirect('admin')  

    return render(request, 'admin/edit_product.html', {
        'product': product,
        'categories': categories,
        'image_fields': image_fields  # Pass image fields to the template
    })

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin')

# Order Views
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin')

# User Views
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin')

# Category Views
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = CategoryForm()
    return render(request, 'admin/add_category.html', {'form': form})

################################################################################


def product_display(request):
    products = Product.objects.all()
    
    return render(request, 'user/product_buy.html', {'products': products})
#_---------------------------cart-------------------------------#
def checkout_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        # Save address
        Address.objects.create(
            user=user,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )

        # Create one order per cart item (with correct quantity)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                amount=item.price,  # already quantity * price in your Cart model
                status="Pending"
            )

        # Clear the cart after purchase
        cart_items.delete()

        return redirect('order_payment2')


def checkout_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        # Save address
        Address.objects.create(
            user=user,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )

        # Create one order per cart item (with correct quantity)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                amount=item.price,  # already quantity * price in your Cart model
                status="Pending"
            )

        # Clear the cart after purchase
        cart_items.delete()

        return redirect('order_summary')

    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def order_summary(request):
    orders = Order.objects.filter(user=request.user)[::-1]

    # Calculate the total price for each order
    for order in orders:
        order.total_price = order.product.price * order.quantity  # Add calculated total price

    # Calculate the total amount for all orders
    total_amount = sum(order.total_price for order in orders)

    return render(request, 'user/order_summary.html', {'orders': orders, 'total_amount': total_amount})

def update_quantity(request, item_id):
    item = get_object_or_404(Cart, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase' and item.quantity < 5:
            item.quantity += 1
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
        item.save()

    return redirect('cart')

# Add to cart functionality
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return redirect('product_not_found')  

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1, 'price': product.price}  # ✅ Fixed: 'price' instead of 'totalprice'
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.price = cart_item.quantity * cart_item.product.price
            cart_item.save()
        
        return redirect('cart')
    else:
        return redirect('signin')

# View cart (standalone template)
def Cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})



def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart')
    
    cart_item.calculate_price()
    cart_item.save()
    return redirect('cart')

# Remove from cart
def remove_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart')



# For implementing Add to Cart button in product detail page
model = SentenceTransformer('all-MiniLM-L6-v2')

def product_detail(request, pk):
    # Fetch the product or return 404
    product = get_object_or_404(Product, id=pk)

    # Initialize context
    cart_product_ids = []
    cart_item_count = 0
    is_reviewed = False
    reviews_list = reviews.objects.filter(pname=product)

    # Handle authenticated user
    if request.user.is_authenticated:
        # Get cart details
        cart_product_ids = list(Cart.objects.filter(user=request.user).values_list('product_id', flat=True))
        cart_item_count = Cart.objects.filter(user=request.user).count()

        # Get user from users model
        try:
            user_profile = users.objects.get(name=request.user)
        except users.DoesNotExist:
            user_profile = None

        if user_profile:
            # Save view history
            ViewHistory.objects.get_or_create(user=user_profile, product=product)

            # Get existing viewed products
            existing_user_data = ViewHistory.objects.filter(user=user_profile)
            existing_products = [history.product.title for history in existing_user_data]

            # Prepare data for vectorization
            data = [{
                'user_id': user_profile.id,
                'product': ','.join(existing_products),
                'search': ''  # Empty search for now
            }]
            df = pd.DataFrame(data)

            # Vectorize and save
            try:
                user_vectors = vectorize_user_with_search(df)
                user_profile.vector_data = json.dumps(user_vectors[0].tolist())
                user_profile.save()
            except Exception as e:
                print(f"Vectorization error: {e}")

            # Check if user has reviewed the product
            is_reviewed = reviews.objects.filter(uname=user_profile, pname=product).exists()

    # Prepare context for template
    context = {
        'product': product,
        'cart_item_count': cart_item_count,
        'cart_product_ids': cart_product_ids,
        'reviews': reviews_list,
        'is_reviewed': is_reviewed,
        'user': request.user,
    }

    return render(request, 'user/product_detail.html', context)

# def addReview(request, pk):
#     if request.method == 'POST':
#         rating = request.POST.get('rating')
#         description = request.POST.get('description')
        
#         # Validate input
#         if not rating or not description:
#             messages.error(request, "Rating and description are required.")
#             return redirect('product_detail', pk=pk)

#         # Validate rating
#         try:
#             rating = int(rating)
#             if rating < 1 or rating > 5:
#                 messages.error(request, "Invalid rating value.")
#                 return redirect('product_detail', pk=pk)
#         except ValueError:
#             messages.error(request, "Rating must be a number.")
#             return redirect('product_detail', pk=pk)

#         # Fetch product
#         product = get_object_or_404(Product, pk=pk)
        
#         # Fetch user profile
#         try:
#             user_profile = users.objects.get(name=request.user)
#         except users.DoesNotExist:
#             messages.error(request, "User profile not found.")
#             return redirect('product_detail', pk=pk)

#         # Check if user has already reviewed this product
#         if reviews.objects.filter(uname=user_profile, pname=product).exists():
#             messages.error(request, "You have already reviewed this product.")
#             return redirect('product_detail', pk=pk)

#         # Create review
#         review = reviews.objects.create(
#             rating=rating,
#             description=description,
#             uname=user_profile,
#             pname=product
#         )

#         # Update product rating
#         rev = reviews.objects.filter(pname=product)
#         total = [i.rating for i in rev]
#         if total:
#             total_rating = round(sum(total) / len(total), 1)
#             product.rating = total_rating
#         else:
#             product.rating = float(rating)
#         product.save()

#         # Update product vector with reviews
#         comments = [i.description for i in rev]
#         pro_data = [{
#             "id": product.id,
#             "title": product.title,
#             "rating": product.rating,
#             "category": product.category.name if product.category else "",
#             "description": product.description,
#             "reviews": ','.join(comments)
#         }]
#         try:
#             df = pd.DataFrame(pro_data)
#             product_vector = vectorize_product_with_reviews(df)
#             product.vector_data = json.dumps(product_vector[0].tolist())
#             product.save()
#         except Exception as e:
#             messages.error(request, "Error processing review data.")
#             return redirect('product_detail', pk=pk)

#         messages.success(request, "Review submitted successfully!")
#         return redirect('product_detail', pk=pk)
#     else:
#         return redirect('product_detail', pk=pk)

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import reviews, Product, users
import pandas as pd
import json
from .vectorize import vectorize_product_with_reviews

def addReview(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to submit a review.")
        return redirect('signin')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        description = request.POST.get('description')
        
        # Validate input
        if not rating or not description:
            messages.error(request, "Rating and description are required.")
            return redirect('product_detail', pk=pk)

        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5.")
                return redirect('product_detail', pk=pk)
        except ValueError:
            messages.error(request, "Rating must be a valid number.")
            return redirect('product_detail', pk=pk)

        # Fetch product
        product = get_object_or_404(Product, pk=pk)
        
        # Fetch user profile
        try:
            user_profile = users.objects.get(name=request.user)
        except users.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('product_detail', pk=pk)

        # Check if user has already reviewed this product
        if reviews.objects.filter(uname=user_profile, pname=product).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect('product_detail', pk=pk)

        # Create review
        try:
            review = reviews.objects.create(
                rating=rating,
                description=description,
                uname=user_profile,
                pname=product
            )
        except Exception as e:
            messages.error(request, f"Error saving review: {str(e)}")
            return redirect('product_detail', pk=pk)

        # Update product rating
        try:
            rev = reviews.objects.filter(pname=product)
            total = [i.rating for i in rev]
            if total:
                total_rating = round(sum(total) / len(total), 1)
                product.rating = total_rating
            else:
                product.rating = float(rating)
            product.save()
        except Exception as e:
            messages.error(request, f"Error updating product rating: {str(e)}")
            return redirect('product_detail', pk=pk)

        # Update product vector with reviews
        try:
            comments = [i.description for i in rev]
            pro_data = [{
                "id": product.id,
                "title": product.title,
                "rating": product.rating,
                "category": product.category.name if product.category else "",
                "description": product.description,
                "reviews": ','.join(comments)
            }]
            df = pd.DataFrame(pro_data)
            product_vector = vectorize_product_with_reviews(df)
            product.vector_data = json.dumps(product_vector[0].tolist())
            product.save()
        except Exception as e:
            messages.error(request, f"Error updating product vector: {str(e)}")
            return redirect('product_detail', pk=pk)

        messages.success(request, "Review submitted successfully!")
        return redirect('product_detail', pk=pk)
    
    return redirect('product_detail', pk=pk)

#----------------------------wishlist------------------------------------------------------#

def wishlist(request):
    
    wishlist_items=Wishlist.objects.filter(user=request.user)
    return render(request, 'user/wishlist.html',{'wishlist_items':wishlist_items}) 


def addtowishlist(request, product_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')
    
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.title} added to your wishlist'
        })
    
    return redirect('home') 
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'user/wishlist.html', context)   



def account(request):
    return render(request, 'accounts/account.html')

def add_address(request,id):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Assign the address to the logged-in user
            address.save()
        return redirect('order_payment', id=id)
    else:
        form = AddressForm()

    return render(request, 'user/add_address.html', {'form': form})

# def address_success(request):
#     return render(request, 'address/address_success.html')







# Order payment view
def order_payment(request, id):
    user = request.user
    user_data = User.objects.get(username=user)
    product = Product.objects.get(pk=id)
    amount = product.discount  # Assuming discount is the correct amount to be charged

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    razorpay_order = client.order.create(
        {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
    )

    order_id = razorpay_order['id']

    # Create order record in the database
    order = Order.objects.create(
        user=user_data, amount=amount, provider_order_id=order_id, product=product, quantity=1
    )
    order.save()

    callback_url = "http://127.0.0.1:8000/razorpay/callback"  
 
    return render(
        request,
        "user/payment.html",
        {
            "callback_url": callback_url,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        },
    )


# Callback view for payment status
@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id

            # Verify the payment signature
            response_data = {
                "razorpay_order_id": provider_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature_id,
            }

            if verify_signature(response_data):
                order.status = PaymentStatus.SUCCESS
                return render (request,"base.html")
            else:
                order.status = PaymentStatus.FAILURE
                print("Signature verification failed")

            order.save()
            return render(request, "base.html", context={"status": order.status})

        else:
            print("Error in callback: Missing Razorpay signature.")
            return render(request, "checkout.html", context={"status": "failure"})

    return render(request, "base.html", context={"status": "invalid_request"})


def order_payment2(request):
    user = request.user
    user_data = User.objects.get(username=user)
    
    # Fetch all cart items for the user
    cart_items = Cart.objects.filter(user=user)
    
    # Calculate total amount for all cart items
    amount = sum(item.price for item in cart_items)  # Assuming price is already calculated

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    razorpay_order = client.order.create(
        {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}  # amount in paise
    )

    order_id = razorpay_order['id']

    # Create order record in the database for each cart item
    for cart_item in cart_items:
        Order.objects.create(
            user=user_data,
            amount=cart_item.price,
            provider_order_id=order_id,
            product=cart_item.product,
            quantity=cart_item.quantity
        )

    # Store the order ID in the session or database if needed
    request.session['order_id'] = order_id

    # Razorpay callback URL (adjust this for your production URL)
    callback_url = "http://127.0.0.1:8000/razorpay/callback2"  
    
    return render(
        request,
        "user/payment2.html",
        {
            "callback_url": callback_url,  # Razorpay callback URL
            "razorpay_key": settings.RAZORPAY_KEY_ID,  # Razorpay key
            "order_id": order_id,  # Razorpay order ID
            "cart_items": cart_items,  # Cart items in the cart
            "total_amount": amount,  # Total amount for the cart (in INR)
            "user_data": user_data,  # User data to prefill form
        }
    )

@csrf_exempt
def callback2(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            return client.utility.verify_payment_signature(response_data)
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            # Using filter instead of get to avoid MultipleObjectsReturned error
            orders = Order.objects.filter(provider_order_id=provider_order_id)
            if orders.exists():
                # If multiple orders exist, we'll process them one by one (or handle your specific case)
                for order in orders:
                    order.payment_id = payment_id
                    order.signature_id = signature_id

                    if verify_signature(request.POST):
                        order.status = PaymentStatus.SUCCESS
                    else:
                        order.status = PaymentStatus.FAILURE
                    
                    order.save()

                return redirect("home")  # Redirect to home page on success
            else:
                return redirect("order_summary")  # Handle the case where no order is found

        elif "error[metadata]" in request.POST:
            try:
                error_data = json.loads(request.POST.get("error[metadata]"))
                provider_order_id = error_data.get("order_id")
                orders = Order.objects.filter(provider_order_id=provider_order_id)
                for order in orders:
                    order.status = PaymentStatus.FAILURE
                    order.save()
            except Exception as e:
                # Optional: log exception
                pass

            return redirect("order_summary")

    return render(request, "home.html")

@login_required
def cancel_order(request, order_id):
    # Fetch the order object
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Update the order status to 'Cancelled'
    order.status = 'Cancelled'
    order.save()

    # Redirect the user to the order summary or home page
    return redirect('order_summary')




def admin(request):
    context = {
        'products': Product.objects.all()[::-1],
        'orders': Order.objects.all()[::-1],

    }
    return render(request, 'admin/admin.html', context)






def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    # Prepare the image fields list for rendering
    image_fields = [
        ('image1', product.image1),
        ('image2', product.image2),
        ('image3', product.image3),
        ('image4', product.image4),
        ('image5', product.image5),
    ]

    if request.method == 'POST':
        # Process form data
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.category_id = request.POST.get('category')
        product.original_price = request.POST.get('original_price')
        product.discount = request.POST.get('discount')
        product.delivery_date = request.POST.get('delivery_date')

        # Update image fields if new files are uploaded
        for i in range(1, 6):
            image_field = f'image{i}'
            uploaded_image = request.FILES.get(image_field)
            if uploaded_image:
                setattr(product, image_field, uploaded_image)

        product.save()  # Save the updated product

        return redirect('admin')  

    return render(request, 'admin/edit_product.html', {
        'product': product,
        'categories': categories,
        'image_fields': image_fields  # Pass image fields to the template
    })

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin')

# Order Views
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin')

# User Views
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin')

# Category Views
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = CategoryForm()
    return render(request, 'admin/add_category.html', {'form': form})

################################################################################

def search1(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()  # Get the search term
        category = request.POST.get('category', '')  # Get the selected category (if any)
        
        # Filter products based on the search term and category
        results = Product.objects.all()
        
        if searched:
            results = results.filter(title__icontains=searched)
        
        if category:
            # Dynamically filter based on the category field
            category_filter = {f"{category}": True}
            results = results.filter(**category_filter)

        return render(request, 'user/search.html', {'searched': searched, 'category': category, 'results': results})
    
    # Render the empty search page for GET requests
    return render(request, 'user/search.html', {'searched': '', 'category': '', 'results': []})

def product_display(request):
    products = Product.objects.all()
    
    return render(request, 'user/product_buy.html', {'products': products})
#_---------------------------cart-------------------------------#
def checkout_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        # Save address
        Address.objects.create(
            user=user,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )

        # Create one order per cart item (with correct quantity)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                amount=item.price,  # already quantity * price in your Cart model
                status="Pending"
            )

        # Clear the cart after purchase
        cart_items.delete()

        return redirect('order_payment2')


def checkout_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        # Save address
        Address.objects.create(
            user=user,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )

        # Create one order per cart item (with correct quantity)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                amount=item.price,  # already quantity * price in your Cart model
                status="Pending"
            )

        # Clear the cart after purchase
        cart_items.delete()

        return redirect('order_summary')

    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def order_summary(request):
    orders = Order.objects.filter(user=request.user)[::-1]

    # Calculate the total price for each order
    for order in orders:
        order.total_price = order.product.price * order.quantity  # Add calculated total price

    # Calculate the total amount for all orders
    total_amount = sum(order.total_price for order in orders)

    return render(request, 'user/order_summary.html', {'orders': orders, 'total_amount': total_amount})

def update_quantity(request, item_id):
    item = get_object_or_404(Cart, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase' and item.quantity < 5:
            item.quantity += 1
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
        item.save()

    return redirect('cart')

# Add to cart functionality
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return redirect('product_not_found')  

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1, 'price': product.price}  # ✅ Fixed: 'price' instead of 'totalprice'
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.price = cart_item.quantity * cart_item.product.price
            cart_item.save()
        
        return redirect('cart')
    else:
        return redirect('signin')

# View cart (standalone template)
def Cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})



def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart')
    
    cart_item.calculate_price()
    cart_item.save()
    return redirect('cart')

# Remove from cart
def remove_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart')



# For implementing Add to Cart button in product detail page
# def product_detail(request, pk):
#     product = get_object_or_404(Product, id=pk)  # Changed from filter() to get_object_or_404()
#     cart_product_ids = []
    
#     if request.user.is_authenticated:
#         cart_product_ids = list(Cart.objects.filter(user=request.user).values_list('product_id', flat=True))
#         cart_item_count = Cart.objects.filter(user=request.user).count()
#     else:
#         cart_item_count = 0 
    
#     context = {
#         'product': product,
#         'cart_item_count': cart_item_count,
#         'cart_product_ids': cart_product_ids
#     }
#     return render(request, 'user/product_detail.html', context)



def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    cart_product_ids = []
    cart_item_count = 0
    is_reviewed = False
    reviews_list = reviews.objects.filter(pname=product)

    if request.user.is_authenticated:
        cart_product_ids = list(Cart.objects.filter(user=request.user).values_list('product_id', flat=True))
        cart_item_count = Cart.objects.filter(user=request.user).count()
        try:
            user_profile = users.objects.get(name=request.user)
        except users.DoesNotExist:
            user_profile = None
        if user_profile:
            ViewHistory.objects.get_or_create(user=user_profile, product=product)
            existing_user_data = ViewHistory.objects.filter(user=user_profile)
            existing_products = [history.product.title for history in existing_user_data]
            data = [{
                'user_id': user_profile.id,
                'product': ','.join(existing_products),
                'search': ''
            }]
            df = pd.DataFrame(data)
            try:
                user_vectors = vectorize_user_with_search(df)
                user_profile.vector_data = json.dumps(user_vectors[0].tolist())
                user_profile.save()
            except Exception as e:
                print(f"Vectorization error: {e}")
            is_reviewed = reviews.objects.filter(uname=user_profile, pname=product).exists()

    context = {
        'product': product,
        'cart_item_count': cart_item_count,
        'cart_product_ids': cart_product_ids,
        'reviews': reviews_list,
        'is_reviewed': is_reviewed,
        'user': request.user,
    }
    return render(request, 'user/product_detail.html', context)

#----------------------------wishlist------------------------------------------------------#

def wishlist(request):
    
    wishlist_items=Wishlist.objects.filter(user=request.user)
    return render(request, 'user/wishlist.html',{'wishlist_items':wishlist_items}) 


def addtowishlist(request, product_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')
    
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.title} added to your wishlist'
        })
    
    return redirect('home') 
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'user/wishlist.html', context)   



def account(request):
    return render(request, 'accounts/account.html')

def add_address(request,id):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Assign the address to the logged-in user
            address.save()
        return redirect('order_payment', id=id)
    else:
        form = AddressForm()

    return render(request, 'user/add_address.html', {'form': form})

# def address_success(request):
#     return render(request, 'address/address_success.html')







# Order payment view
def order_payment(request, id):
    user = request.user
    user_data = User.objects.get(username=user)
    product = Product.objects.get(pk=id)
    amount = product.discount  # Assuming discount is the correct amount to be charged

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    razorpay_order = client.order.create(
        {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
    )

    order_id = razorpay_order['id']

    # Create order record in the database
    order = Order.objects.create(
        user=user_data, amount=amount, provider_order_id=order_id, product=product, quantity=1
    )
    order.save()

    callback_url = "http://127.0.0.1:8000/razorpay/callback"  
 
    return render(
        request,
        "user/payment.html",
        {
            "callback_url": callback_url,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        },
    )


# Callback view for payment status
@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id

            # Verify the payment signature
            response_data = {
                "razorpay_order_id": provider_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature_id,
            }

            if verify_signature(response_data):
                order.status = PaymentStatus.SUCCESS
                return render (request,"base.html")
            else:
                order.status = PaymentStatus.FAILURE
                print("Signature verification failed")

            order.save()
            return render(request, "base.html", context={"status": order.status})

        else:
            print("Error in callback: Missing Razorpay signature.")
            return render(request, "checkout.html", context={"status": "failure"})

    return render(request, "base.html", context={"status": "invalid_request"})


def order_payment2(request):
    user = request.user
    user_data = User.objects.get(username=user)
    
    # Fetch all cart items for the user
    cart_items = Cart.objects.filter(user=user)
    
    # Calculate total amount for all cart items
    amount = sum(item.price for item in cart_items)  # Assuming price is already calculated

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    razorpay_order = client.order.create(
        {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}  # amount in paise
    )

    order_id = razorpay_order['id']

    # Create order record in the database for each cart item
    for cart_item in cart_items:
        Order.objects.create(
            user=user_data,
            amount=cart_item.price,
            provider_order_id=order_id,
            product=cart_item.product,
            quantity=cart_item.quantity
        )

    # Store the order ID in the session or database if needed
    request.session['order_id'] = order_id

    # Razorpay callback URL (adjust this for your production URL)
    callback_url = "http://127.0.0.1:8000/razorpay/callback2"  
    
    return render(
        request,
        "user/payment2.html",
        {
            "callback_url": callback_url,  # Razorpay callback URL
            "razorpay_key": settings.RAZORPAY_KEY_ID,  # Razorpay key
            "order_id": order_id,  # Razorpay order ID
            "cart_items": cart_items,  # Cart items in the cart
            "total_amount": amount,  # Total amount for the cart (in INR)
            "user_data": user_data,  # User data to prefill form
        }
    )

@csrf_exempt
def callback2(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            return client.utility.verify_payment_signature(response_data)
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            # Using filter instead of get to avoid MultipleObjectsReturned error
            orders = Order.objects.filter(provider_order_id=provider_order_id)
            if orders.exists():
                # If multiple orders exist, we'll process them one by one (or handle your specific case)
                for order in orders:
                    order.payment_id = payment_id
                    order.signature_id = signature_id

                    if verify_signature(request.POST):
                        order.status = PaymentStatus.SUCCESS
                    else:
                        order.status = PaymentStatus.FAILURE
                    
                    order.save()

                return redirect("home")  # Redirect to home page on success
            else:
                return redirect("order_summary")  # Handle the case where no order is found

        elif "error[metadata]" in request.POST:
            try:
                error_data = json.loads(request.POST.get("error[metadata]"))
                provider_order_id = error_data.get("order_id")
                orders = Order.objects.filter(provider_order_id=provider_order_id)
                for order in orders:
                    order.status = PaymentStatus.FAILURE
                    order.save()
            except Exception as e:
                # Optional: log exception
                pass

            return redirect("order_summary")

    return render(request, "home.html")

@login_required
def cancel_order(request, order_id):
    # Fetch the order object
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Update the order status to 'Cancelled'
    order.status = 'Cancelled'
    order.save()

    # Redirect the user to the order summary or home page
    return redirect('order_summary')