import pytest
import stripe
from django.contrib.messages import get_messages
from django.urls import reverse
from django.contrib.auth.models import User

from KomodoreApp.models import Profile, Car, Product, CartItem, Order


@pytest.mark.django_db
def test_buyer_registration_view_valid(client, registration_data):
    url = reverse("buyer_register")
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, registration_data, follow=True)
    assert response.status_code == 200
    assert User.objects.filter(username=registration_data["username"]).exists()
    assert Profile.objects.filter(user__username=registration_data["username"], is_buyer=True).exists()


@pytest.mark.django_db
def test_buyer_registration_view_invalid(client):
    url = reverse("buyer_register")
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, {}, follow=True)
    assert response.status_code == 200
    assert "This field is required" in response.content.decode()


@pytest.mark.django_db
def test_seller_registration_view_valid(client, registration_data):
    url = reverse("seller_register")
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, registration_data, follow=True)
    assert response.status_code == 200
    assert User.objects.filter(username=registration_data["username"]).exists()
    assert Profile.objects.filter(user__username=registration_data["username"], is_seller=True).exists()


@pytest.mark.django_db
def test_seller_registration_view_invalid(client):
    url = reverse("seller_register")
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, {}, follow=True)
    assert response.status_code == 200
    assert "This field is required" in response.content.decode()


@pytest.mark.django_db
def test_login_view_valid(client, test_user):
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200

    data = {"username": test_user.username, "password": "testpassword"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("home")


@pytest.mark.django_db
def test_login_view_invalid(client, test_user):
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200

    data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert b'Invalid username or password. Please try again.' in response.content


@pytest.mark.django_db
def test_home_view_buyer(client, test_buyer_profile):
    url = reverse("home")
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Find Auto Parts for Your Vehicle' in response.content


@pytest.mark.django_db
def test_home_view_seller(client, test_seller_profile):
    url = reverse("home")
    client.login(username=test_seller_profile.user.username, password="testpassword")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Sell auto parts from anywhere' in response.content


@pytest.mark.django_db
def test_about_view_authenticated(client, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("about")
    response = client.get(url)

    assert response.status_code == 200
    assert b'About Komodore' in response.content


@pytest.mark.django_db
def test_about_view_unauthenticated(client):
    url = reverse("about")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('about')}"


@pytest.mark.django_db
def test_contact_view_authenticated(client, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("contact")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Contact Us' in response.content


@pytest.mark.django_db
def test_contact_view_unauthenticated(client):
    url = reverse("contact")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('contact')}"


@pytest.mark.django_db
def test_profile_view_buyer(client, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("profile_view")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Buyer' in response.content


@pytest.mark.django_db
def test_profile_view_seller(client, test_seller_profile):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    url = reverse("profile_view")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Seller' in response.content


@pytest.mark.django_db
def test_profile_view_unauthenticated(client):
    url = reverse("profile_view")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('profile_view')}"


@pytest.mark.django_db
def test_car_search_post(client, create_test_cars, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("car_search")
    response = client.post(url, {"manufacturer": "Volkswagen", "model": "Golf", "year": 2024})

    assert response.status_code == 302
    assert response.url == reverse("part_search_with_car", kwargs={
        "car_id": Car.objects.get(manufacturer="Volkswagen", model="Golf", year=2024).pk})


@pytest.mark.django_db
def test_car_search_get(client, create_test_cars, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("car_search")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Volkswagen' in response.content
    assert b'Mercedes' in response.content


@pytest.mark.django_db
def test_part_search_authenticated(client, create_test_cars, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("part_search")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Search By Part' in response.content


@pytest.mark.django_db
def test_part_search_unauthenticated(client):
    url = reverse("part_search")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('part_search')}"


@pytest.mark.django_db
def test_part_search_with_car_authenticated(client, create_test_cars, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    car_id = Car.objects.first().id
    url = reverse("part_search_with_car", kwargs={"car_id": car_id})
    response = client.get(url)

    assert response.status_code == 200
    assert b'Search By Part' in response.content
    assert b'Volkswagen' in response.content


@pytest.mark.django_db
def test_part_search_with_car_unauthenticated(client, create_test_cars):
    car_id = Car.objects.first().id
    url = reverse("part_search_with_car", kwargs={"car_id": car_id})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('part_search_with_car', kwargs={'car_id': car_id})}"


@pytest.mark.django_db
def test_item_list_view_without_car_authenticated(client, new_product, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("item_list_without_car", kwargs={"category": new_product.category})
    response = client.get(url)

    assert response.status_code == 200
    assert new_product.name.encode() in response.content
    assert str(round(new_product.price, 2)).encode() in response.content
    assert new_product.category.encode() in response.content


@pytest.mark.django_db
def test_item_list_view_with_car_authenticated(client, new_product, new_car, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_product.cars.add(new_car)
    url = reverse("item_list", kwargs={"category": new_product.category, "car_id": 1})
    response = client.get(url)

    assert response.status_code == 200
    assert new_product.name.encode() in response.content
    assert str(round(new_product.price, 2)).encode() in response.content
    assert new_product.category.encode() in response.content


@pytest.mark.django_db
def test_add_view_authenticated_buyer(client, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("add")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse("login")


@pytest.mark.django_db
def test_add_view_authenticated_seller_valid(client, test_seller_profile, product_data):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    url = reverse("add")
    product_data["seller"] = test_seller_profile.user
    response = client.post(url, data=product_data)

    assert response.status_code == 302
    assert response.url == reverse("seller_parts")


@pytest.mark.django_db
def test_add_view_authenticated_seller_invalid(client, test_seller_profile, product_data):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    url = reverse("add")
    product_data["seller"] = test_seller_profile.user
    product_data["quantity"] = 0
    response = client.post(url, data=product_data)

    assert response.status_code == 200
    assert b'Add a new product' in response.content


@pytest.mark.django_db
def test_add_view_unauthenticated(client):
    url = reverse("add")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('add')}"


@pytest.mark.django_db
def test_seller_parts_view_authenticated(client, test_seller_profile, new_product, new_car):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    new_product.cars.add(new_car)
    new_product.seller = test_seller_profile.user
    new_product.save()
    url = reverse("seller_parts")
    response = client.get(url)

    assert response.status_code == 200
    assert b'Your Products' in response.content
    assert new_product.name.encode() in response.content
    assert str(round(new_product.price, 2)).encode() in response.content


@pytest.mark.django_db
def test_seller_parts_view_unauthenticated(client):
    url = reverse("seller_parts")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('seller_parts')}"


@pytest.mark.django_db
def test_part_details_view_authenticated_buyer(client, test_buyer_profile, new_product, new_shopping_cart):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.save()
    url = reverse("part_details", args=[new_product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert new_product.name.encode() in response.content
    assert str(round(new_product.price, 2)).encode() in response.content in response.content


@pytest.mark.django_db
def test_part_details_view_authenticated_seller(client, test_seller_profile, new_product):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    url = reverse("part_details", args=[new_product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert new_product.name.encode() in response.content
    assert str(round(new_product.price, 2)).encode() in response.content in response.content


@pytest.mark.django_db
def test_part_details_view_unauthenticated(client, new_product):
    url = reverse("part_details", args=[new_product.id])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('part_details', args=[new_product.id])}"


@pytest.mark.django_db
def test_remove_product_view_authenticated_seller(client, test_seller_profile, new_product):
    client.login(username=test_seller_profile.user.username, password="testpassword")
    new_product.seller = test_seller_profile.user
    new_product.save()
    url = reverse("remove_product", args=[new_product.id])
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("seller_parts")
    assert not Product.objects.filter(id=new_product.id).exists()


@pytest.mark.django_db
def test_remove_product_view_unauthenticated(client, new_product):
    url = reverse("remove_product", args=[new_product.id])
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('remove_product', args=[new_product.id])}"


@pytest.mark.django_db
def test_update_quantity_view_post(client, test_buyer_profile, new_product):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("update_quantity", args=[new_product.id])
    response = client.post(url, {"new_quantity": 5})

    assert response.status_code == 200
    assert {"success": True} == response.json()


@pytest.mark.django_db
def test_update_quantity_view_get(client, test_buyer_profile, new_product):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("update_quantity", args=[new_product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert {"success": False} == response.json()


@pytest.mark.django_db
def test_add_to_cart(client, test_buyer_profile, new_product):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("add_to_cart", args=[new_product.id])
    response = client.post(url, {"quantity": new_product.quantity - 1})

    assert response.status_code == 302
    assert response.url == reverse("home")

    cart_item = CartItem.objects.get(shoppingcart__user=test_buyer_profile.user, product=new_product)
    assert cart_item.quantity == new_product.quantity - 1


@pytest.mark.django_db
def test_remove_from_cart(client, test_buyer_profile, new_shopping_cart, new_cart_item):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    url = reverse("remove_from_cart", args=[new_cart_item.id])
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("shopping_cart")

    with pytest.raises(CartItem.DoesNotExist):
        CartItem.objects.get(id=new_cart_item.id)


@pytest.mark.django_db
def test_shopping_cart(client, test_buyer_profile, new_shopping_cart, new_cart_item):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    url = reverse("shopping_cart")
    response = client.get(url)

    assert response.status_code == 200
    assert "cart_items" in response.context
    assert "total" in response.context

    assert new_cart_item.product.name.encode() in response.content
    assert str(round(new_cart_item.product.price, 2) * new_cart_item.quantity).encode() in response.content
    assert str(new_cart_item.quantity).encode() in response.content


@pytest.mark.django_db
def test_checkout_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    product = new_cart_item.product
    new_shopping_cart.save()
    url = reverse("checkout")
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("shipping_information", kwargs={"order_id": Order.objects.first().pk})
    assert Order.objects.filter(user=test_buyer_profile.user).exists()

    quantity = product.quantity
    product.refresh_from_db()
    assert product.quantity == quantity-new_cart_item.quantity


@pytest.mark.django_db
def test_checkout_insufficient_quantity_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    product = new_cart_item.product
    product.quantity = new_cart_item.quantity - 1
    product.save()
    new_shopping_cart.save()
    url = reverse("checkout")
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("shopping_cart")

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "Insufficient quantity available for some products."


@pytest.mark.django_db
def test_checkout_unauthenticated(client):
    url = reverse("checkout")
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('checkout')}"


@pytest.mark.django_db
def test_checkout_get(client, test_buyer_profile, new_shopping_cart, new_cart_item):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    url = reverse("checkout")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse("shopping_cart")


@pytest.mark.django_db
def test_shipping_information_post_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item, new_order, shipping_data):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("shipping_information", kwargs={"order_id": new_order.pk})
    response = client.post(url, data=shipping_data)

    assert response.status_code == 302
    assert response.url == reverse("payment_method", kwargs={"order_id": new_order.pk})
    new_order.refresh_from_db()
    assert new_order.shipping_address == shipping_data["shipping_address"]
    assert new_order.shipping_note == shipping_data["shipping_note"]
    assert new_order.shipping_city == shipping_data["shipping_city"]
    assert new_order.shipping_postal_code == shipping_data["shipping_postal_code"]
    assert new_order.shipping_country == shipping_data["shipping_country"]


@pytest.mark.django_db
def test_shipping_information_invalid_post_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item, new_order):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("shipping_information", kwargs={"order_id": new_order.pk})
    response = client.post(url, data={})

    assert response.status_code == 200
    assert "form" in response.context
    assert b'Shipping Information' in response.content


@pytest.mark.django_db
def test_payment_method_authenticated(client, test_buyer_profile, new_order):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("payment_method", kwargs={"order_id": new_order.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert "order" in response.context


@pytest.mark.django_db
def test_process_payment_online_authenticated(client, test_buyer_profile, new_order):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("process_payment", kwargs={"order_id": new_order.pk})
    response = client.post(url, data={"payment_method": "online"})

    assert response.status_code == 302
    assert response.url == reverse("stripe_payment", kwargs={"order_id": new_order.pk})
    new_order.refresh_from_db()
    assert new_order.payment_method == "Online"


@pytest.mark.django_db
def test_process_payment_cash_authenticated(client, test_buyer_profile, new_order):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("process_payment", kwargs={"order_id": new_order.pk})
    response = client.post(url, data={"payment_method": "cash"})

    assert response.status_code == 302
    assert response.url == reverse("order_confirmed")
    new_order.refresh_from_db()
    assert new_order.payment_method == "Cash on Delivery"


@pytest.mark.django_db
def test_stripe_payment_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item, new_order, monkeypatch):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    new_order.user = test_buyer_profile.user
    new_order.payment_method = "Online"
    new_order.save()

    def mock_stripe_charge_create(*args, **kwargs):
        class MockCharge:
            id = "mock_charge_id"

        return MockCharge()

    monkeypatch.setattr("stripe.Charge.create", mock_stripe_charge_create)

    url = reverse("stripe_payment", kwargs={"order_id": new_order.pk})
    response = client.post(url, data={"stripeToken": "mock_token"})

    assert response.status_code == 302
    assert response.url == reverse("order_confirmed")

    new_order.refresh_from_db()
    assert new_order.payment_status == "Paid"


@pytest.mark.django_db
def test_stripe_payment_invalid_authenticated(client, test_buyer_profile, new_shopping_cart, new_cart_item, new_order, monkeypatch):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    new_order.user = test_buyer_profile.user
    new_order.save()

    def mock_stripe_charge_create(*args, **kwargs):
        raise stripe.error.StripeError("Mock Stripe Error")

    monkeypatch.setattr("stripe.Charge.create", mock_stripe_charge_create)

    url = reverse("stripe_payment", kwargs={"order_id": new_order.pk})
    response = client.post(url, data={"stripeToken": "mock_token"})

    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Mock Stripe Error"


@pytest.mark.django_db
def test_stripe_payment_get(client, test_buyer_profile, new_shopping_cart, new_cart_item, new_order):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    new_shopping_cart.user = test_buyer_profile.user
    new_shopping_cart.cart_items.add(new_cart_item)
    new_shopping_cart.save()
    new_order.user = test_buyer_profile.user
    new_order.save()
    url = reverse("stripe_payment", kwargs={"order_id": new_order.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert "order" in response.context


@pytest.mark.django_db
def test_order_confirmed_authenticated(client, test_buyer_profile):
    client.login(username=test_buyer_profile.user.username, password="testpassword")
    url = reverse("order_confirmed")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["is_buyer"] == test_buyer_profile.is_buyer
    assert response.context["is_seller"] == test_buyer_profile.is_seller


@pytest.mark.django_db
def test_order_confirmed_unauthenticated(client):
    url = reverse("order_confirmed")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('order_confirmed')}"
