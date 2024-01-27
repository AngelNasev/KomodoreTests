import json

import pytest
from django.urls import reverse

from KomodoreApp.models import Car


@pytest.mark.django_db
def test_get_models(client, create_test_cars):
    url = reverse("get_models")

    response = client.get(url, {"manufacturer": "Volkswagen"})
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert set(data) == {"Golf", "Passat"}


@pytest.mark.django_db
def test_get_models_no_manufacturer(client, create_test_cars):
    url = reverse("get_models")

    response = client.get(url)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert len(set(data)) == 0


@pytest.mark.django_db
def test_get_years(client, create_test_cars):
    url = reverse("get_years")

    response = client.get(url, {"manufacturer": "Volkswagen", "model": "Golf"})
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert set(data) == {car.year for car in Car.objects.filter(manufacturer="Volkswagen", model="Golf")}


@pytest.mark.django_db
def test_get_years_no_model(client, create_test_cars):
    url = reverse("get_years")

    response = client.get(url, {"manufacturer": "Volkswagen"})
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert len(set(data)) == 0


@pytest.mark.django_db
def test_get_years_no_model_no_manufacturer(client, create_test_cars):
    url = reverse("get_years")

    response = client.get(url)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert len(set(data)) == 0
