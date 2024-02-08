import pytest

from KomodoreApp.forms import RegistrationForm, LoginForm, AddProductForm, ShippingInformationForm


# RegistrationForm tests
@pytest.mark.django_db
def test_empty_registration_form():
    form = RegistrationForm(data={})
    assert not form.is_valid()

    for field_name, field in form.fields.items():
        if field.required:
            assert f"This field is required." in form.errors[field_name]


@pytest.mark.django_db
@pytest.mark.parametrize("data, validity, error_field, error_message", [
    ({"username": "user1", "email": "user1@example.com", "password1": "testpassword", "password2": "testpassword"}, True, None, None),
    ({"username": "user2", "email": "user2@example.com", "password1": "testpassword", "password2": "mismatchedpassword"}, False, "password2", "The two password fields didn’t match."),
    ({"username": "existinguser", "email": "testuser@example.com", "password1": "testpassword", "password2": "testpassword"}, False, "username", "Username is already taken."),
])
def test_registration_form(user_factory, data, validity, error_field, error_message):
    user = user_factory(username="existinguser", email="testuser@example.com", password="testpassword")
    form = RegistrationForm(data=data)

    assert form.is_valid() == validity

    if error_field:
        assert error_field in form.errors
        assert form.errors[error_field][0] == error_message


# LoginForm tests
@pytest.mark.django_db
def test_empty_login_form():
    form = LoginForm(data={})
    assert not form.is_valid()

    for field_name, field in form.fields.items():
        if field.required:
            assert f"This field is required." in form.errors[field_name]


@pytest.mark.django_db
@pytest.mark.parametrize("data, validity, error_field, error_message", [
    ({"username": "user1", "password": "testpassword"}, True, None, None),
    ({"username": None, "password": "testpassword"}, False, "username", "Username is required."),
    ({"username": "user1", "password": None}, False, "password", "Password is required."),
])
def test_login_form(data, validity, error_field, error_message):
    form = LoginForm(data=data)

    assert form.is_valid() == validity

    if error_field:
        assert error_field in form.errors
        assert form.errors[error_field][1] == error_message


# AddProductForm tests
@pytest.mark.django_db
def test_empty_add_product_form():
    form = AddProductForm(data={})
    assert not form.is_valid()

    for field_name, field in form.fields.items():
        if field.required:
            assert f"This field is required." in form.errors[field_name]


@pytest.mark.django_db
@pytest.mark.parametrize("data, validity, error_field, error_message", [
    ({"name": "Test Product", "quantity": 10, "price": 25.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, True, None, None),
    ({"name": None, "quantity": 5, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "name", "This field is required."),
    ({"name": "Test Product", "quantity": None, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "quantity", "This field is required."),
    ({"name": "Test Product", "quantity": 0, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "quantity", "Quantity must be greater than or equal to 1."),
    ({"name": "Test Product", "quantity": 1, "price": None, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "price", "This field is required."),
    ({"name": "Test Product", "quantity": 1, "price": 0, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "price", "Price must be greater than or equal to 0.01."),
    ({"name": "Test Product", "quantity": 1, "price": 0.001, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "price", "Ensure that there are no more than 2 decimal places."),
    ({"name": "Test Product", "quantity": 1, "price": 10.99, "image": None, "characteristics": None, "description": "Test description", "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "characteristics", "This field is required."),
    ({"name": "Test Product", "quantity": 1, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": None, "category": "Batteries", "warranty": "1 Year Warranty", "cars": []}, False, "description", "This field is required."),
    ({"name": "Test Product", "quantity": 1, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": None, "warranty": "1 Year Warranty", "cars": []}, False, "category", "This field is required."),
    ({"name": "Test Product", "quantity": 1, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": None, "cars": []}, False, "warranty", "This field is required."),
    ({"name": "Test Product", "quantity": 1, "price": 10.99, "image": None, "characteristics": "Test characteristics", "description": "Test description", "category": "Batteries", "warranty": "1", "cars": []}, False, "warranty", "Select a valid choice. 1 is not one of the available choices."),
])
def test_add_product_form(new_user, new_car, data, validity, error_field, error_message):
    seller = new_user
    car = new_car
    data["cars"] = [car]
    form = AddProductForm(data=data)
    form.instance.seller = seller

    assert form.is_valid() == validity

    if error_field:
        assert error_field in form.errors
        assert form.errors[error_field][0] == error_message


# ShippingInformationForm tests
@pytest.mark.django_db
@pytest.mark.parametrize("data, validity, error_field, error_message", [
    ({"shipping_address": "Test Address", "shipping_note": "Test Note", "shipping_city": "Test City", "shipping_postal_code": "12345", "shipping_country": "Test Country"}, True, None, None),
    ({"shipping_address": None, "shipping_note": "Test Note", "shipping_city": "Test City", "shipping_postal_code": "12345", "shipping_country": "Test Country"}, False, "shipping_address", "This field is required."),
    ({"shipping_address": "Short", "shipping_note": "Test Note", "shipping_city": "Test City", "shipping_postal_code": "12345", "shipping_country": "Test Country"}, False, "shipping_address", "Shipping address is too short."),
    ({"shipping_address": "Test Address", "shipping_note": "Test Note", "shipping_city": None, "shipping_postal_code": "12345", "shipping_country": "Test Country"}, False, "shipping_city", "This field is required."),
    ({"shipping_address": "Test Address", "shipping_note": "Test Note", "shipping_city": "123City", "shipping_postal_code": "12345", "shipping_country": "Test Country"}, False, "shipping_city", "Shipping city must contain only letters."),
])
def test_shipping_information_form(data, validity, error_field, error_message):
    form = ShippingInformationForm(data=data)

    assert form.is_valid() == validity

    if error_field:
        assert error_field in form.errors
        assert form.errors[error_field][0] == error_message


@pytest.mark.django_db
def test_empty_shipping_information_form():
    form = ShippingInformationForm(data={})
    assert not form.is_valid()

    for field_name, field in form.fields.items():
        if field.required:
            assert f"This field is required." in form.errors[field_name]
