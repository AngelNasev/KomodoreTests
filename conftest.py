import io

import pytest
from PIL import Image
from django.contrib.auth.models import User
from pytest_factoryboy import register

from KomodoreApp.models import Car
from KomodoreApp.tests.factories import CarFactory, UserFactory, ProductFactory, ProfileFactory, CartItemFactory, \
    ShoppingCartFactory, OrderItemFactory, OrderFactory

register(CarFactory)
register(UserFactory)
register(ProductFactory)
register(ProfileFactory)
register(CartItemFactory)
register(ShoppingCartFactory)
register(OrderItemFactory)
register(OrderFactory)


@pytest.fixture
def new_car(db, car_factory):
    car = car_factory.create()
    return car


@pytest.fixture
def new_user(db, user_factory):
    user = user_factory.create()
    return user


@pytest.fixture
def new_product(db, product_factory):
    product = product_factory.create()
    return product


@pytest.fixture
def new_profile(db, profile_factory):
    profile = profile_factory.create()
    return profile


@pytest.fixture
def new_cart_item(db, cart_item_factory):
    cart_item = cart_item_factory.create()
    return cart_item


@pytest.fixture
def new_shopping_cart(db, shopping_cart_factory):
    shopping_cart = shopping_cart_factory.create()
    return shopping_cart


@pytest.fixture
def new_order_item(db, order_item_factory):
    order_item = order_item_factory.create()
    return order_item


@pytest.fixture
def new_order(db, order_factory):
    order = order_factory.create()
    return order


@pytest.fixture
def registration_data(db):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password1": "testpassword",
        "password2": "testpassword",
    }
    return data


@pytest.fixture
def test_user(db):
    username = 'testuser'
    password = 'testpassword'
    return User.objects.create_user(username=username, password=password)


@pytest.fixture
def test_buyer_profile(db, profile_factory, test_user):
    return profile_factory.create(user=test_user, is_buyer=True, is_seller=False)


@pytest.fixture
def test_seller_profile(db, profile_factory, test_user):
    return profile_factory.create(user=test_user, is_buyer=False, is_seller=True)


@pytest.fixture
def create_test_cars(db, car_factory):
    manufacturer_model_combinations = [
        {"manufacturer": "Volkswagen", "model": "Golf"},
        {"manufacturer": "Volkswagen", "model": "Passat"},
        {"manufacturer": "Mercedes", "model": "C-Class"},
        {"manufacturer": "Mercedes", "model": "E-Class"},
    ]
    all_years = [2024, 2023, 2022, 2021, 2020]

    for combination in manufacturer_model_combinations:
        for year in all_years:
            car_factory.create(manufacturer=combination["manufacturer"], model=combination["model"], year=year)


def create_fake_image():
    width, height = 100, 100
    color = (255, 255, 255)
    image = Image.new('RGB', (width, height), color)

    image_bytes_io = io.BytesIO()
    image.save(image_bytes_io, format='JPEG')
    image_bytes = image_bytes_io.getvalue()

    return image_bytes


@pytest.fixture
def product_data(db, create_test_cars):
    cars = Car.objects.all()
    car_ids = list(cars.values_list('id', flat=True))

    return {
        "seller": None,
        "name": "Test Product",
        "price": 25.99,
        "quantity": 10,
        "image": create_fake_image(),
        "warranty": "1 Year Warranty",
        "characteristics": "Test characteristics",
        "description": "Test description",
        "cars": car_ids,
        "category": "Batteries",
    }


@pytest.fixture
def shipping_data(db):
    return {
        "shipping_address": "Test Address",
        "shipping_note": "Test Note",
        "shipping_city": "Test City",
        "shipping_postal_code": "12345",
        "shipping_country": "Test Country"
    }
