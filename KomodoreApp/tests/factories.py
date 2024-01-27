from datetime import datetime

import factory
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from faker import Faker
from KomodoreApp.models import Car, Product, Profile, CartItem, ShoppingCart, OrderItem, Order

fake = Faker()


class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car

    manufacturer = fake.company()
    model = fake.word()
    year = fake.date_between_dates(date_start=datetime(2015, 1, 1), date_end=datetime(2019, 12, 31)).year


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user_{n}")
    email = fake.email()
    password = factory.PostGenerationMethodCall("set_password", fake.password())


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        skip_postgeneration_save = True

    seller = factory.SubFactory(UserFactory)
    name = fake.word()
    price = Decimal(fake.random_number(digits=5) / 100)
    quantity = fake.random_int(min=1, max=100)
    image = factory.LazyAttribute(
        lambda _: ContentFile(open("data/images/example.jpg", "rb").read(), "example.jpg")
    )
    warranty = fake.random_element(elements=["No Warranty", "1 Year Warranty", "2 Year Warranty", "Lifetime Warranty"])
    characteristics = fake.text()
    description = fake.text()
    category = fake.random_element(elements=["Batteries", "Engine Oil", "Antifreeze", "Fuel Lines", "Exhaust",
                                             "Windshield Wipers", "Brakes", "Engine Parts", "Tires", "Wheel Mountings"])

    @factory.post_generation
    def cars(self, create, extracted):
        if not create:
            return

        if extracted:
            for car in extracted:
                self.cars.add(car)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    is_buyer = fake.boolean()
    is_seller = fake.boolean()


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    quantity = fake.random_int(min=1, max=10)


class ShoppingCartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShoppingCart
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def cart_items(self, create, extracted):
        if not create:
            return

        if extracted:
            for item in extracted:
                self.cart_items.add(item)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    product = factory.SubFactory(ProductFactory)
    quantity = fake.random_int(min=1, max=10)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory)
    payment_status = fake.random_element(elements=["Pending", "Paid"])
    payment_method = fake.random_element(elements=["Online", "Cash"])
    shipping_address = fake.address()
    shipping_note = fake.text()
    shipping_city = fake.city()
    shipping_postal_code = fake.zipcode()
    shipping_country = fake.country()

    @factory.post_generation
    def order_items(self, create, extracted):
        if not create:
            return

        if extracted:
            for item in extracted:
                self.order_items.add(item)
