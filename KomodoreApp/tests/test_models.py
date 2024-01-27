import pytest
from decimal import Decimal

from django.db.models import Sum, F
from django.db.utils import IntegrityError

from KomodoreApp.models import Car, Product, Profile, CartItem, ShoppingCart, OrderItem, Order, get_admin_user


# Admin tests
@pytest.mark.django_db
def test_get_admin_user(user_factory):
    # Create an admin user for the test
    admin_user = user_factory(username="admin", is_staff=True, is_superuser=True)

    # Call the function
    result = get_admin_user()

    # Assert that the returned user is the same as the one created
    assert result == admin_user


# Car Tests
@pytest.mark.django_db
def test_new_car(new_car):
    car = new_car
    count = Car.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_car_model_str(new_car):
    assert str(new_car) == f"{new_car.manufacturer} {new_car.model} {new_car.year}"


@pytest.mark.django_db
@pytest.mark.parametrize("manufacturer, model, year, validity", [
    ("Manufacturer", "Model", 2001, True),
    ("Manufacturer", "Model", -1, False),
    ("Manufacturer", "Model", None, False),
    ("Manufacturer", None, 2001, False),
    (None, "Model", 2001, False),
])
def test_car_creation(car_factory, manufacturer, model, year, validity):
    if validity:
        test = car_factory(manufacturer=manufacturer, model=model, year=year)

        count = Car.objects.all().count()
        assert count == 1
        assert test.manufacturer == manufacturer
        assert test.model == model
        assert test.year == year
    else:
        with pytest.raises(IntegrityError):
            car_factory(manufacturer=manufacturer, model=model, year=year)


# Product tests
@pytest.mark.django_db
def test_new_product(new_product):
    product = new_product
    count = Product.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_product_model_str(new_product):
    assert str(new_product) == f"{new_product.name}"


@pytest.mark.django_db
@pytest.mark.parametrize("name, price, quantity, warranty, characteristics, description, category, validity", [
    ("Test Product", Decimal("19.99"), 10, "1 Year Warranty", "Characteristic 1", "Description 1", "Engine Oil", True),
    (None, Decimal("19.99"), 10, "1 Year Warranty", "Characteristic 1", "Description 1", "Engine Oil", False),
    ("Test Product", None, 10, "1 Year Warranty", "Characteristic 1", "Description 1", "Engine Oil", False),
    ("Test Product", Decimal("19.99"), None, "1 Year Warranty", "Characteristic 1", "Description 1", "Engine Oil",
     False),
    ("Test Product", Decimal("19.99"), 10, None, "Characteristic 1", "Description 1", "Engine Oil", False),
])
def test_product_creation(product_factory, new_car, name, price, quantity, warranty, characteristics, description,
                          category, validity):
    car = new_car

    if validity:
        test = product_factory(
            name=name,
            price=price,
            quantity=quantity,
            warranty=warranty,
            characteristics=characteristics,
            description=description,
            category=category,
            cars=[car]
        )

        count = Product.objects.all().count()
        assert count == 1
        assert test.name == name
        assert test.price == price
        assert test.quantity == quantity
        assert test.warranty == warranty
        assert test.characteristics == characteristics
        assert test.description == description
        assert test.category == category
    else:
        with pytest.raises(IntegrityError):
            product_factory(
                name=name,
                price=price,
                quantity=quantity,
                warranty=warranty,
                characteristics=characteristics,
                description=description,
                category=category,
                cars=[car]
            )


# Profile tests
@pytest.mark.django_db
def test_new_profile(new_profile):
    profile = new_profile
    count = Profile.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_profile_model_str(new_profile):
    assert str(new_profile) == f"{new_profile.user.username}"


@pytest.mark.django_db
@pytest.mark.parametrize("is_buyer, is_seller, validity", [
    (True, True, True),
    (None, True, False),
    (False, None, False),
], )
def test_profile_creation(profile_factory, new_user, is_buyer, is_seller, validity):
    user = new_user

    if validity:
        test = profile_factory(
            user=user,
            is_buyer=is_buyer,
            is_seller=is_seller
        )

        count = Profile.objects.all().count()
        assert count == 1
        assert test.user == user
        assert test.is_buyer == is_buyer
        assert test.is_seller == is_seller
    else:
        with pytest.raises(IntegrityError):
            profile_factory(
                user=user,
                is_buyer=is_buyer,
                is_seller=is_seller
            )


# Cart Item tests
@pytest.mark.django_db
def test_new_cart_item(new_cart_item):
    cart_item = new_cart_item
    count = CartItem.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_cart_item_model_str(new_cart_item):
    assert str(new_cart_item) == f"{new_cart_item.quantity} of {new_cart_item.product.name}"


@pytest.mark.django_db
def test_cart_item_model_total(new_cart_item):
    assert new_cart_item.total() == float(new_cart_item.product.price * int(new_cart_item.quantity))


@pytest.mark.django_db
@pytest.mark.parametrize("quantity, validity", [
    (1, True),
    (None, False),
    (-1, False),
], )
def test_cart_item_creation(cart_item_factory, new_product, quantity, validity):
    product = new_product

    if validity:
        test = cart_item_factory(
            product=product,
            quantity=quantity
        )

        count = CartItem.objects.all().count()
        assert count == 1
        assert test.product == product
        assert test.quantity == quantity
    else:
        with pytest.raises(IntegrityError):
            cart_item_factory(
                product=product,
                quantity=quantity
            )


# Shopping cart tests
@pytest.mark.django_db
def test_new_shopping_cart(new_shopping_cart):
    shopping_cart = new_shopping_cart
    count = ShoppingCart.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_shopping_cart_model_str(new_shopping_cart):
    assert str(new_shopping_cart) == f"{new_shopping_cart.user.username}'s Cart"


# Order Item tests
@pytest.mark.django_db
def test_new_order_item(new_order_item):
    order_item = new_order_item
    count = OrderItem.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_order_item_model_str(new_order_item):
    assert str(new_order_item) == f"{new_order_item.quantity} of {new_order_item.product.name}"


@pytest.mark.django_db
def test_order_item_model_total(new_order_item):
    assert new_order_item.total() == float(new_order_item.product.price * int(new_order_item.quantity))


@pytest.mark.django_db
@pytest.mark.parametrize("quantity, validity", [
    (1, True),
    (None, False),
    (-1, False),
], )
def test_order_item_creation(order_item_factory, new_product, quantity, validity):
    product = new_product

    if validity:
        test = order_item_factory(
            product=product,
            quantity=quantity
        )

        count = OrderItem.objects.all().count()
        assert count == 1
        assert test.product == product
        assert test.quantity == quantity
    else:
        with pytest.raises(IntegrityError):
            order_item_factory(
                product=product,
                quantity=quantity
            )


# Order tests
@pytest.mark.django_db
def test_new_order(new_order):
    order = new_order
    count = Order.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_order_model_str(new_order):
    assert str(new_order) == f"Order by {new_order.user.username} on {new_order.order_date}"


@pytest.mark.django_db
def test_order_model_total(new_order, new_order_item):
    order = new_order
    order_item = new_order_item
    order.order_items.add(order_item)
    total = order.order_items.aggregate(order_total=Sum(F("product__price") * F("quantity")))["order_total"]
    assert order.total() == total


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payment_status, payment_method, shipping_address, shipping_note, "
    "shipping_city, shipping_postal_code, shipping_country, validity",
    [
        ("Pending", "Online", "Address 1", "Note 1", "City 1", "12345", "Country 1", True),
        (None, "Online", "Address 1", "Note 1", "City 1", "12345", "Country 1", False),
        ("Pending", None, "Address 1", "Note 1", "City 1", "12345", "Country 1", False),
        ("Pending", "Online", None, "Note 1", "City 1", "12345", "Country 1", False),
        ("Pending", "Online", "Address 1", None, "City 1", "12345", "Country 1", False),
        ("Pending", "Online", "Address 1", "Note 1", None, "12345", "Country 1", False),
        ("Pending", "Online", "Address 1", "Note 1", "City 1", None, "Country 1", False),
        ("Pending", "Online", "Address 1", "Note 1", "City 1", "12345", None, False),

    ], )
def test_order_creation(order_factory, new_user, new_order_item, payment_status, payment_method, shipping_address,
                        shipping_note, shipping_city, shipping_postal_code, shipping_country, validity):
    user = new_user
    order_item = new_order_item

    if validity:
        test_order = order_factory(
            user=user,
            order_items=[order_item],
            payment_status=payment_status,
            payment_method=payment_method,
            shipping_address=shipping_address,
            shipping_note=shipping_note,
            shipping_city=shipping_city,
            shipping_postal_code=shipping_postal_code,
            shipping_country=shipping_country
        )

        count = Order.objects.all().count()
        assert count == 1
        assert test_order.user == user
        assert test_order.order_items.count() == 1
        assert test_order.payment_status == payment_status
        assert test_order.payment_method == payment_method
        assert test_order.shipping_address == shipping_address
        assert test_order.shipping_note == shipping_note
        assert test_order.shipping_city == shipping_city
        assert test_order.shipping_postal_code == shipping_postal_code
        assert test_order.shipping_country == shipping_country
    else:
        with pytest.raises(IntegrityError):
            order_factory(
                user=user,
                order_items=[order_item],
                payment_status=payment_status,
                payment_method=payment_method,
                shipping_address=shipping_address,
                shipping_note=shipping_note,
                shipping_city=shipping_city,
                shipping_postal_code=shipping_postal_code,
                shipping_country=shipping_country
            )
