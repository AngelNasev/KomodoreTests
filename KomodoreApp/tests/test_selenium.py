import os
import time

import pytest
from django.test import LiveServerTestCase
from selenium.webdriver import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Komodore.settings import BASE_DIR


@pytest.mark.django_db
@pytest.mark.usefixtures("browser")
class TestBuyer(LiveServerTestCase):

    @pytest.mark.django_db
    def test_buyer_e2e(self):
        self.driver.get("http://127.0.0.1:8000/login/")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")

        username_input.send_keys("test_buyer")
        password_input.send_keys("Test123!")
        self.driver.find_element(By.ID, "id_submit").click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "buyer_profile"))
        ).click()

        time.sleep(1)
        initial_num_orders = len(self.driver.find_elements(By.CLASS_NAME, "list-group-item"))

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='navbarNav-1']/ul/li[1]/a"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='home-title']"), "Find Auto Parts for Your Vehicle")
        )

        self.driver.find_element(By.XPATH, "//*[@id='box']/div[2]/a[1]").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h2[@class='search-title opacity-1']"), "Please enter your car’s manufacturer")
        )

        manufacturer_dropdown = Select(self.driver.find_element(By.ID, "manufacturer-dropdown"))
        model_dropdown = Select(self.driver.find_element(By.ID, "model-dropdown"))
        year_dropdown = Select(self.driver.find_element(By.ID, "year-dropdown"))

        manufacturer_dropdown.select_by_visible_text("Mercedes")
        time.sleep(0.1)
        model_dropdown.select_by_visible_text("S-Class")
        time.sleep(0.1)
        year_dropdown.select_by_visible_text("2020")
        time.sleep(0.1)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "shop-button"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='car']"), "Mercedes S-Class 2020")
        )

        self.driver.find_element(By.XPATH, "//*[@id='box-1']/div[1]/div[1]/a").click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "card"))
        )
        card_count = len(self.driver.find_elements(By.CLASS_NAME, "card"))
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='category']"), "Batteries")
        )
        assert card_count == 1

        self.driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/a").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='part-name']"), "DURACELL Premium")
        )

        self.driver.find_element(By.XPATH, "//button[@class='quantity-btn plus-btn btn btn-outline-primary']").click()
        quantity_value = self.driver.find_element(By.ID, "quantity").get_attribute("value")
        assert int(quantity_value) == 2

        self.driver.find_element(By.XPATH, "//button[@class='add-to-cart']").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='go-to-cart']"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div/table/tbody/tr/td[3]"))
        )
        item_price_text = self.driver.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[3]").text
        item_price = float(item_price_text.replace("$", "").replace(" ", ""))
        item_quantity = float(self.driver.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[4]").text)
        total_text = self.driver.find_element(By.XPATH, "/html/body/div/table/tbody/tr/td[5]").text
        total = float(total_text.replace("$", "").replace(" ", ""))
        assert item_price * item_quantity == total

        self.driver.find_element(By.XPATH, "//button[@class='check-out']").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h3[@class='box-title']"), "Shipping Information")
        )

        shipping_address_input = self.driver.find_element(By.ID, "id_shipping_address")
        shipping_note_input = self.driver.find_element(By.ID, "id_shipping_note")
        shipping_city_input = self.driver.find_element(By.ID, "id_shipping_city")
        shipping_postal_code_input = self.driver.find_element(By.ID, "id_shipping_postal_code")
        shipping_country_input = self.driver.find_element(By.ID, "id_shipping_country")

        shipping_address_input.send_keys("Test address 1/1")
        shipping_note_input.send_keys("Test shipping note")
        shipping_city_input.send_keys("Bitola")
        shipping_postal_code_input.send_keys("7000")
        shipping_country_input.send_keys("North Macedonia")
        self.driver.find_element(By.XPATH, "//button[@class='submit-btn mx-auto my-4']").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='home-title']"), "Choose a payment option")
        )

        self.driver.find_element(By.XPATH, "//button[@class='option-btn mx-auto mb-3']").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//p[@class='blue']"), "Please enter your card details:")
        )

        self.driver.find_element(By.XPATH, "//button[@class='stripe-button-el']").click()
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/iframe"))
        )
        time.sleep(1)
        stripe_email_input = self.driver.find_element(By.ID, "email")
        stripe_card_number = self.driver.find_element(By.ID, "card_number")
        stripe_expiration = self.driver.find_element(By.ID, "cc-exp")
        stripe_cvc = self.driver.find_element(By.ID, "cc-csc")

        stripe_email_input.send_keys("test@gmail.com")
        for digit in "4242424242424242":
            stripe_card_number.send_keys(digit)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of(stripe_card_number)
            )
        stripe_expiration.send_keys("12")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(stripe_expiration)
        )
        stripe_expiration.send_keys("34")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(stripe_cvc)
        )
        stripe_cvc.send_keys("123")
        self.driver.find_element(By.ID, "submitButton").click()

        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='order-confirmed']"), "Order Confirmed")
        )

        self.driver.find_element(By.ID, "buyer_profile").click()
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "list-group-item"))
        )
        order_list = self.driver.find_elements(By.CLASS_NAME, "list-group-item")
        assert len(order_list) == initial_num_orders + 1


@pytest.mark.django_db
@pytest.mark.usefixtures("browser")
class TestSeller(LiveServerTestCase):

    @pytest.mark.django_db
    def test_seller_e2e(self):
        self.driver.get("http://127.0.0.1:8000/login/")

        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")

        username_input.send_keys("test_seller")
        password_input.send_keys("Test123!")
        self.driver.find_element(By.ID, "id_submit").click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='navbarNav-2']/ul/li[2]/a"))
        ).click()

        time.sleep(1)
        initial_num_products = len(self.driver.find_elements(By.CLASS_NAME, "card"))

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='navbarNav-2']/ul/li[1]/a"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*[@id='box']/div[1]"), "Sell auto parts from anywhere")
        )

        self.driver.find_element(By.XPATH, "//*[@id='box']/div[2]/a[1]").click()

        product_name_input = self.driver.find_element(By.ID, "id_name")
        price_input = self.driver.find_element(By.ID, "id_price")
        quantity_input = self.driver.find_element(By.ID, "id_quantity")
        image_input = self.driver.find_element(By.ID, "id_image")
        warranty_element = self.driver.find_element(By.ID, "id_warranty")
        warranty_dropdown = Select(warranty_element)
        characteristics_input = self.driver.find_element(By.ID, "id_characteristics")
        description_input = self.driver.find_element(By.ID, "id_description")
        cars_element = self.driver.find_element(By.ID, "id_cars")
        cars_dropdown = Select(cars_element)
        category_element = self.driver.find_element(By.ID, "id_category")
        category_dropdown = Select(category_element)

        image_path = os.path.join(BASE_DIR, 'data/images/castrol_oil.jpg')

        product_name_input.send_keys("Castrol Edge 5w-30")
        price_input.send_keys("20")
        quantity_input.send_keys("5")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(image_input)
        )
        image_input.send_keys(image_path)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(warranty_element)
        )
        warranty_dropdown.select_by_visible_text("No Warranty")
        characteristics_input.send_keys("Castrol characteristics")
        description_input.send_keys("Castrol description")
        cars_dropdown.select_by_visible_text("Mercedes S-Class 2020")
        cars_dropdown.select_by_visible_text("Mercedes G-Class 2018")
        cars_dropdown.select_by_visible_text("Audi A1 2016")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(category_element)
        )
        category_dropdown.select_by_visible_text("Engine Oil")
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-button"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "num-available"), "5 Available")
        )
        card_count = len(self.driver.find_elements(By.CLASS_NAME, "card"))
        num_available = self.driver.find_element(By.ID, "num-available").text
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//h2[@class='category']"), "Your Products")
        )
        assert num_available == "5 Available"
        assert card_count == initial_num_products + 1

        self.driver.find_element(By.XPATH, "//a[@class='more-info inter']").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "quantityBtn"))
        ).click()
        new_quantity = self.driver.find_element(By.ID, "newQuantity")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(new_quantity)
        )
        for _ in range(5):
            new_quantity.send_keys(Keys.ARROW_DOWN)

        self.driver.find_element(By.ID, "updateBtn").click()
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "navbarNav-2"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "not-in-stock-text"), "Not in Stock")
        )
