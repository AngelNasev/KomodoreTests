"""
URL configuration for Komodore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import path

from KomodoreApp.views import buyer_registration, seller_registration, home, login_view, car_search, part_search, \
    get_models, get_years, item_list, add, seller_parts, part_details, add_to_cart, shopping_cart, remove_from_cart, \
    checkout, shipping_information, payment_method, process_payment, stripe_payment, order_confirmed, about, contact, \
    update_quantity, profile_view, remove_product

urlpatterns = [
    path('', lambda request: redirect('home'), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('buyer/register/', buyer_registration, name='buyer_register'),
    path('seller/register/', seller_registration, name='seller_register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('home/', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('profile/', profile_view, name='profile_view'),
    path('get_models/', get_models, name='get_models'),
    path('get_years/', get_years, name='get_years'),
    path('search/car', car_search, name='car_search'),
    path('search/part', part_search, name='part_search'),
    path('search/part/<int:car_id>', part_search, name='part_search_with_car'),
    path('item_list/<str:category>/<int:car_id>/', item_list, name='item_list'),
    path('item_list/<str:category>/', item_list, name='item_list_without_car'),
    path('add/', add, name='add'),
    path('seller/parts', seller_parts, name='seller_parts'),
    path('details/<int:product_id>/', part_details, name='part_details'),
    path('update_quantity/<int:product_id>/', update_quantity, name='update_quantity'),
    path('remove_product/<int:product_id>/', remove_product, name='remove_product'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('shopping_cart/', shopping_cart, name='shopping_cart'),
    path('checkout/', checkout, name='checkout'),
    path('shipping_information/<int:order_id>', shipping_information, name='shipping_information'),
    path('payment_method/<int:order_id>', payment_method, name='payment_method'),
    path('process_payment/<int:order_id>', process_payment, name='process_payment'),
    path('stripe_payment/<int:order_id>', stripe_payment, name='stripe_payment'),
    path('order_confirmed/', order_confirmed, name='order_confirmed')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
