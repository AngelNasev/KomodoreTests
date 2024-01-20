import stripe
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from Komodore import settings
from KomodoreApp.forms import RegistrationForm, LoginForm, AddProductForm, ShippingInformationForm
from KomodoreApp.models import Profile, Car, Product, ShoppingCart, CartItem, Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def buyer_registration(request):
    context = {"form": RegistrationForm()}
    if request.method == "POST":
        form_data = RegistrationForm(data=request.POST, files=request.FILES)
        if form_data.is_valid():
            user = form_data.save(commit=False)
            password = form_data.cleaned_data.get('password1')
            user.set_password(password)
            user.save()
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                profile = Profile()
                profile.user = user
                profile.is_buyer = True
                profile.is_seller = False
                profile.save()
                shopping_cart = ShoppingCart(user=user)
                shopping_cart.save()
                return redirect("home")
        else:
            context["form"] = form_data

    return render(request, "buyer_registration.html", context=context)


def seller_registration(request):
    context = {"form": RegistrationForm()}

    if request.method == "POST":
        form_data = RegistrationForm(data=request.POST, files=request.FILES)
        if form_data.is_valid():
            user = form_data.save(commit=False)
            password = form_data.cleaned_data.get('password1')
            user.set_password(password)
            user.save()
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                profile = Profile()
                profile.user = user
                profile.is_buyer = False
                profile.is_seller = True
                profile.save()
                return redirect("home")
        else:
            context["form"] = form_data

    return render(request, "seller_registration.html", context=context)


def login_view(request):
    context = {"form": LoginForm()}

    if request.method == "POST":
        form_data = LoginForm(data=request.POST, files=request.FILES)
        if form_data.is_valid():
            username = form_data.cleaned_data.get('username')
            password = form_data.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, "login.html", context=context)


@login_required(login_url="/login/")
def home(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    if profile.is_buyer:
        return render(request, "buyer_home.html", context=context)
    if profile.is_seller:
        return render(request, "seller_home.html", context=context)


@login_required(login_url="/login/")
def about(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    return render(request, "about.html", context=context)


@login_required(login_url="/login/")
def contact(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    return render(request, "contact.html", context=context)


@login_required(login_url="/login/")
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    user_orders = Order.objects.filter(user=request.user).all()
    context = {"profile": profile,
               "is_buyer": profile.is_buyer,
               "is_seller": profile.is_seller,
               "orders": user_orders}
    return render(request, 'profile.html', context=context)


def get_models(request):
    manufacturer = request.GET.get('manufacturer')
    models = Car.objects.filter(manufacturer=manufacturer).values_list('model', flat=True)
    return JsonResponse(list(models), safe=False)


def get_years(request):
    manufacturer = request.GET.get('manufacturer')
    model = request.GET.get('model')
    years = Car.objects.filter(manufacturer=manufacturer, model=model).values_list('year', flat=True)
    return JsonResponse(list(years), safe=False)


@login_required(login_url="/login/")
def car_search(request):
    if request.method == "POST":
        selected_manufacturer = request.POST.get('manufacturer')
        selected_model = request.POST.get('model')
        selected_year = request.POST.get('year')
        car = Car.objects.filter(manufacturer=selected_manufacturer, model=selected_model, year=selected_year).get()
        return redirect('part_search_with_car', car_id=car.pk)

    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    manufacturers = Car.objects.values_list('manufacturer', flat=True).distinct()
    context["manufacturers"] = manufacturers
    return render(request, "search_by_car.html", context=context)


@login_required(login_url="/login/")
def part_search(request, car_id=None):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    if car_id:
        car = get_object_or_404(Car, pk=car_id)
        context["car"] = car

    return render(request, "search_by_part.html", context=context)


@login_required(login_url="/login/")
def item_list(request, category, car_id=None):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    if car_id:
        car = get_object_or_404(Car, pk=car_id)
        parts = Product.objects.filter(cars=car, category=category)
        context["parts"] = parts
    else:
        parts = Product.objects.filter(category=category)
        context["parts"] = parts
    context["category"] = category
    return render(request, "item_list.html", context=context)


@login_required(login_url="/login/")
def add(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller, "form": AddProductForm()}
    if profile.is_seller:
        if request.method == "POST":
            form_data = AddProductForm(data=request.POST, files=request.FILES)
            if form_data.is_valid():
                product = form_data.save(commit=False)
                product.seller = request.user
                product.image = form_data.cleaned_data["image"]
                product.save()
                return redirect("seller_parts")
            else:
                context["form"] = form_data
    else:
        return redirect("/login/")
    return render(request, "add.html", context=context)


@login_required(login_url="/login/")
def seller_parts(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller,
               "parts": Product.objects.filter(seller=request.user).all()}
    return render(request, "seller_parts.html", context=context)


@login_required(login_url="/login/")
def part_details(request, product_id):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    part = get_object_or_404(Product, pk=product_id)
    context["part"] = part
    is_in_cart = False
    if profile.is_buyer:
        cart = ShoppingCart.objects.get(user=request.user)
        is_in_cart = cart.cart_items.filter(product=part).exists()
    context["is_in_cart"] = is_in_cart

    return render(request, "part_details.html", context=context)


@login_required(login_url="/login/")
def remove_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    product.delete()
    return redirect("seller_parts")


@login_required(login_url="/login/")
def update_quantity(request, product_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('new_quantity', 1))
        product = get_object_or_404(Product, pk=product_id)
        product.quantity = new_quantity
        product.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required(login_url="/login/")
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)

        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        cart_item, created = cart.cart_items.get_or_create(product=product)
        cart_item.quantity = quantity
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url="/login/")
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        cart = get_object_or_404(ShoppingCart, user=request.user)
        cart_item = cart.cart_items.get(id=cart_item_id)
        cart_item.delete()
    return redirect('shopping_cart')


@login_required(login_url="/login/")
def shopping_cart(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}

    cart = ShoppingCart.objects.get(user=request.user)
    cart_items = cart.cart_items.select_related('product')
    context["cart_items"] = cart_items

    total = cart_items.annotate(
        item_total=F('product__price') * F('quantity')
    ).aggregate(cart_total=Sum('item_total'))['cart_total'] or 0

    context["total"] = total

    return render(request, "shopping_cart.html", context=context)


@login_required(login_url="/login/")
def checkout(request):
    if request.method == 'POST':
        cart = ShoppingCart.objects.get(user=request.user)
        order = Order.objects.create(user=request.user)
        order.payment_status = 'Pending'
        order.save()

        for cart_item in cart.cart_items.all():
            product = cart_item.product
            if product.quantity >= cart_item.quantity:
                order_item, created = order.order_items.get_or_create(product=product, quantity=cart_item.quantity)
                order_item.save()
                product.quantity -= cart_item.quantity
                product.save()
                cart_item.delete()
            else:
                messages.error(request, "Insufficient quantity available for some products.")
                return redirect('shopping_cart')
        return redirect('shipping_information', order_id=order.pk)

    return redirect('shopping_cart')


@login_required(login_url="/login/")
def shipping_information(request, order_id):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer,
               "is_seller": profile.is_seller,
               "form": ShippingInformationForm()}

    order = get_object_or_404(Order, pk=order_id)
    context["order"] = order
    if request.method == 'POST':
        form_data = ShippingInformationForm(data=request.POST)
        if form_data.is_valid():
            order.shipping_address = form_data.cleaned_data["shipping_address"]
            order.shipping_note = form_data.cleaned_data["shipping_note"]
            order.shipping_city = form_data.cleaned_data["shipping_city"]
            order.shipping_postal_code = form_data.cleaned_data["shipping_postal_code"]
            order.shipping_country = form_data.cleaned_data["shipping_country"]
            order.save()
            return redirect('payment_method', order_id=order.pk)
        else:
            context["form"] = form_data

    return render(request, "shipping_information.html", context=context)


@login_required(login_url="/login/")
def payment_method(request, order_id):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}
    order = get_object_or_404(Order, pk=order_id)
    context["order"] = order
    return render(request, "payment_method.html", context=context)


@login_required(login_url="/login/")
def process_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    method = request.POST.get('payment_method')
    if method == "online":
        order.payment_method = "Online"
        order.save()
        return redirect('stripe_payment', order_id=order_id)
    elif method == 'cash':
        order.payment_method = "Cash on Delivery"
        order.save()
        return redirect('order_confirmed')


@login_required(login_url="/login/")
def stripe_payment(request, order_id):
    profile = Profile.objects.get(user=request.user)
    order = get_object_or_404(Order, pk=order_id)
    total = order.order_items.annotate(
        item_total=F('product__price') * F('quantity')
    ).aggregate(order_total=Sum('item_total'))['order_total'] or 0

    context = {
        "is_buyer": profile.is_buyer,
        "is_seller": profile.is_seller,
        'order': order,
        'total_amount': int(total * 100),
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    }

    if request.method == 'POST':
        try:
            payment_intent = stripe.Charge.create(
                amount=int(total * 100),
                currency='usd',
                metadata={'order_id': order_id},
                source=request.POST['stripeToken']
            )
            order.payment_status = "Paid"
            order.save()
            return redirect('order_confirmed')
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)})
    return render(request, "stripe_payment.html", context=context)


@login_required(login_url="/login/")
def order_confirmed(request):
    profile = Profile.objects.get(user=request.user)
    context = {"is_buyer": profile.is_buyer, "is_seller": profile.is_seller}

    return render(request, "order_confirmed.html", context=context)
