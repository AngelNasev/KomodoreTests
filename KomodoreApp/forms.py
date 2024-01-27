import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from KomodoreApp.models import Product, Order


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = " form-control w-75 mx-auto"
            field.field.widget.attrs["style"] = "border-radius: 20px; border: 2px solid #2165F6;"
            field.field.widget.attrs["placeholder"] = field.label
            field.label = ""
            field.help_text = ''

            if field.errors:
                field.field.widget.attrs["class"] += " is-invalid"
                field.field.widget.attrs["data-toggle"] = "tooltip"
                field.field.widget.attrs["data-placement"] = "top"
                field.field.widget.attrs["title"] = ", ".join(field.errors)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': ' form-control w-75 mx-auto',
            'style': 'border-radius: 20px; border: 2px solid #2165F6;',
            'placeholder': 'Username',
        }),
        label='',
        help_text='',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': ' form-control w-75 mx-auto',
            'style': 'border-radius: 20px; border: 2px solid #2165F6;',
            'placeholder': 'Password',
        }),
        label='',
        help_text='',
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.errors:
                field.field.widget.attrs["class"] += " is-invalid"
                field.field.widget.attrs["data-toggle"] = "tooltip"
                field.field.widget.attrs["data-placement"] = "top"
                field.field.widget.attrs["title"] = ", ".join(field.errors)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username:
            self.add_error('username', 'Username is required.')

        if not password:
            self.add_error('password', 'Password is required.')

        return cleaned_data


class AddProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = " form-control"
            field.field.widget.attrs["style"] = "border-radius: 20px; border: 2px solid #2165F6;"
            field.field.widget.attrs["placeholder"] = field.label
            field.label = ""
            field.help_text = ""

            if field.errors:
                field.field.widget.attrs["class"] += " is-invalid"
                field.field.widget.attrs["data-toggle"] = "tooltip"
                field.field.widget.attrs["data-placement"] = "top"
                field.field.widget.attrs["title"] = ", ".join(field.errors)

        self.fields["image"].widget.attrs["accept"] = "image/*"
        self.fields["characteristics"].widget.attrs["rows"] = 6
        self.fields["characteristics"].widget.attrs["cols"] = 40
        self.fields["description"].widget.attrs["rows"] = 4
        self.fields["description"].widget.attrs["cols"] = 40
        self.fields["category"].widget.attrs["class"] = "form-select"
        self.fields["warranty"].widget.attrs["class"] = "form-select"

    class Meta:
        model = Product
        exclude = ("seller",)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be greater than or equal to 1.")
        return quantity

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0.01:
            raise forms.ValidationError("Price must be greater than or equal to 0.01.")
        return price


class ShippingInformationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShippingInformationForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = " form-control w-75 mx-auto"
            field.field.widget.attrs["style"] = "border-radius: 20px; border: 2px solid #2165F6;"
            field.field.widget.attrs["placeholder"] = field.label
            field.label = ""
            field.help_text = ""

            if field.errors:
                field.field.widget.attrs["class"] += " is-invalid"
                field.field.widget.attrs["data-toggle"] = "tooltip"
                field.field.widget.attrs["data-placement"] = "top"
                field.field.widget.attrs["title"] = ", ".join(field.errors)

        self.fields["shipping_note"].widget.attrs["rows"] = 4
        self.fields["shipping_note"].widget.attrs["cols"] = 40

    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_note', 'shipping_city', 'shipping_postal_code', 'shipping_country']

    def clean_shipping_address(self):
        shipping_address = self.cleaned_data.get('shipping_address')
        if len(shipping_address) < 10:
            raise forms.ValidationError("Shipping address is too short.")

        return shipping_address

    def clean_shipping_city(self):
        shipping_city = self.cleaned_data.get('shipping_city')
        if not re.match(r'^[A-Za-z\s]+$', shipping_city):
            raise forms.ValidationError("Shipping city must contain only letters.")

        return shipping_city
