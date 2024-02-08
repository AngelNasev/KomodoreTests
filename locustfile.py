import os
import random

from locust import HttpUser, between, task

from Komodore.settings import BASE_DIR


class BuyerClient(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.get("/login/")
        csrf_token = response.cookies.get("csrftoken", "")

        login_data = {
            "username": "locust_buyer",
            "password": "Test123!",
            "csrfmiddlewaretoken": csrf_token,
        }
        self.client.post("/login/", data=login_data)

    @task
    def buyer_home(self):
        self.client.get("/home/")
        self.client.get("/about/")
        self.client.get("/contact/")
        self.client.get("/profile/")
        self.client.get("/shopping_cart/")

    @task
    def buyer_search(self):
        self.client.get("/search/car")
        self.client.get("/search/part")
        self.client.get("/search/part/1")
        self.client.get("/search/car?manufacturer=Mercedes&model=S-Class&year=2020")
        self.client.get("/item_list/Engine%20Oil/1/")
        self.client.get("/details/1/")

    @task
    def add_to_cart(self):
        self.client.get("/add_to_cart/1/")
        data_add = {
            "quantity": 1
        }
        self.client.post("/add_to_cart/1/", data=data_add, allow_redirects=True)

    @task
    def checkout(self):
        self.client.get("/checkout/")
        self.client.get("/shipping_information/1")
        self.client.get("/payment_method/1")
        self.client.get("/shipping_information/1")

        self.client.post("/process_payment/1", data={"payment_method": "online"})

        self.client.get("/stripe_payment/1")
        self.client.get("/order_confirmed/")


class SellerClient(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.get("/login/")
        csrf_token = response.cookies.get("csrftoken", "")

        login_data = {
            "username": "locust_seller",
            "password": "Test123!",
            "csrfmiddlewaretoken": csrf_token,
        }

        self.client.post("/login/", data=login_data)

    @task
    def seller_home(self):
        self.client.get("/home/")
        self.client.get("/about/")
        self.client.get("/contact/")
        self.client.get("/profile/")

    @task
    def seller_parts(self):
        self.client.get("/seller/parts")
        self.client.get("/item_list/Engine%20Oil/")

    @task
    def add_product(self):
        response = self.client.get("/add/")
        csrf_token = response.cookies.get("csrftoken", "")
        image_path = os.path.join(BASE_DIR, "data/images/castrol_oil.jpg")
        image_file = open(image_path, "rb")
        data = {
            "name": "Castrol Edge 5w-30",
            "price": 20,
            "quantity": 5,
            "warranty": "No Warranty",
            "characteristics": "Castrol characteristics",
            "description": "Castrol description",
            "cars": ["Mercedes S-Class 2020", "Mercedes G-Class 2018", "Audi A1 2016"],
            "category": "Engine Oil",
            "csrfmiddlewaretoken": csrf_token,
        }
        files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
        self.client.post("/add/", data=data, files=files)
        image_file.close()

    @task
    def update_quantity(self):
        new_quantity = random.randint(0, 10)

        response = self.client.get("/update_quantity/36/")
        csrf_token = response.cookies.get("csrftoken", "")
        data = {
            "new_quantity": new_quantity,
            "csrfmiddlewaretoken": csrf_token,
        }

        self.client.post(f"/update_quantity/36/", data=data)