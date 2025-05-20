from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.signin, name='signin'),  # Ensure this line is here
    path('cart/', views.Cart_view, name='cart'),
    path('remove_from_cart/<id>',views.remove_from_cart,name='remove_from_cart'),
    path('signup',views.signup,name='signup'),
    path('orders',views.orders,name='orders'),
    path('help',views.help,name='help'),
    path('logout',views.userlogout,name='userlogout'),
    path('search/', views.search_func, name='search_func'),






    path('product_buy',views.product_buy,name='product_buy'),   
    path('wheretobuy',views.wheretobuy,name='wheretobuy'),
    path('buy-now<int:product_id>/', views.buy_now, name='buy_now'),
    # Change this line
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('product_details/<int:pk>/',views.product_detail, name='product_detail'),   
    path('account',views.account,name='account'),
    # path('product')


#######admin#####
    path('dashboard', views.admin, name='admin'), 
    path('order',views.order,name='order'),

    path('add_product',views.add_product,name='add_product'),

    path('edit_product/<int:product_id>/',views.edit_product,name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),


    
    path('address',views.address,name='address'),

#____________________wishlist___________________________#
    path('wishlist',views.wishlist,name='wishlist'),
    path('addtowishlist/<int:product_id>/', views.addtowishlist, name='addtowishlist'),
    path('remove-from-wishlist/<int:product_id>/',views.remove_from_wishlist, name='remove_from_wishlist'),
    
# payments
    path('order_payment/<int:id>', views.order_payment, name='order_payment'),
    path('razorpay/callback', views.callback, name='callback'),
    path('order_payment2',views.order_payment2,name='order_payment2'),
    path('razorpay/callback2',views.callback2,name='callback2'),
    path('add_address/<id>/', views.add_address, name='add_address'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('order_summary',views.order_summary,name='order_summary'),



    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),

    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
     path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),




    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
