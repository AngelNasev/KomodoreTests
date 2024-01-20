from django.contrib import admin

from KomodoreApp.models import Car, Product, Profile, ShoppingCart, Order, OrderItem

# Register your models here.
admin.site.register(Car)
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(OrderItem)
