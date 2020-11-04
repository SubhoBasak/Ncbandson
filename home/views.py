from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from . import models
from . import forms
from .paytm_checksum import generate_checksum, verify_checksum
import random


SERVER_MAIL = 'ncbandsons@ncbandsons.in'
INFO_MAIL = 'subhobasak50@gmail.com'
MID = 'LbPvcx56694639417098'
MKEY = 'kzBi8M6rEJ1HNR#d'
WEBSITE = 'WEBSTAGING'
INDUSTRY_TYPE = 'Retail'
CHANNEL_ID = 'WEB'


def index_view(request):
    prod_s = []
    categories = models.Category.objects.all()
    if 'sel_cat' in request.POST:
        if request.POST['sel_cat'] == '__all__':
            prod_s = models.Product.objects.all()
        else:
            try:
                sel_cat = models.Category.objects.get(id=request.POST['sel_cat'])
                prod_s = models.Product.objects.filter(category=sel_cat)
            except models.Category.DoesNotExist:
                prod_s = models.Product.objects.all()
    else:
        prod_s = models.Product.objects.all()
    return render(request, 'index.html',
                  {'categories': categories,
                   'prod_s': prod_s},
                  status=200)


def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


def contact_us_view(request):
    query_status = -1
    if 'qs' in request.GET:
        query_status = int(request.GET.get('qs'))
    if 'new_query' in request.POST:
        form = forms.ContactUsForm(request.POST)
        query_status = 0
        if form.is_valid():
            form.save()
            send_mail('NEW CONTACT US QUERY', 'Details: http://ncbandsons.in/admin/home/contactus/{}/change/'.format(form.id), SERVER_MAIL,
                      ['info@ncbandsons.in'])
            query_status = 1
        return redirect(reverse('contact_us')+'?qs='+str(query_status))
    return render(request, 'contact-us.html', {'query_status': query_status}, status=200)


def authentication(request):
    status = 0
    if 'sign_in_now' in request.POST:
        try:
            cur_user = User.objects.get(email=request.POST['email'])
            if cur_user.check_password(request.POST['password']):
                login(request, cur_user)
                return redirect(reverse('index'))
        except User.DoesNotExist:
            status = 2
        else:
            status = 1
    elif 'sign_up_now' in request.POST:
        try:
            cur_user = User.objects.get(email=request.POST['email'])
            status = 3
        except User.DoesNotExist:
            cur_user = User(username=request.POST['email'], email=request.POST['email'])
            cur_user.set_password(request.POST['password'])
            cur_user.save()
            login(request, cur_user)
            return redirect(reverse('index'))
    return render(request, 'login.html', {'status': status})


def about_us_view(request):
    return render(request, 'about_us.html', status=200)


def detail_view(request, pid):
    try:
        main_prod = models.Product.objects.get(id=pid)
    except models.Product.DoesNotExist:
        return redirect(reverse('index'))
    if 'buy_now' in request.POST:
        if request.user.is_authenticated:
            this_order = models.Order(user=request.user, oid='ORDID'+timezone.now().strftime('%Y%m%d%H%M%S')+str(request.user.id))
            this_order.save()
            prod_list = models.ProductList(order=this_order, product=main_prod, quantity=1, price=main_prod.discounted_price)
            prod_list.save()
            this_order.total = prod_list.price
            this_order.save()
            return redirect('/add_address/'+str(this_order.oid)+'/')
        else:
            return redirect(reverse('auth_url'))
    elif 'add_to_cart' in request.POST:
        pass
    image_s = models.ProductImages.objects.filter(prod=main_prod)
    spec_s = models.ProductSpecification.objects.filter(prod=main_prod)
    rel_prod_s = models.RelatedProduct.objects.filter(prod=main_prod)
    return render(request, 'details_page.html',
                  {'main_prod': main_prod, 'image_s': image_s, 'spec_s': spec_s, 'rel_prod_s': rel_prod_s},
                  status=200)


@login_required
def add_to_cart(request, pid):
    try:
        prod = models.Product.objects.get(id=pid)
    except models.Product.DoesNotExist:
        return redirect(reverse('index'))
    try:
        cart_obj = models.Cart.objects.get(user=request.user, product=prod)
    except models.Cart.DoesNotExist:
        cart_obj = models.Cart(user=request.user, product=prod)
        cart_obj.save()
    return redirect(reverse('cart'))


@login_required
def cart_view(request):
    cart_items = models.Cart.objects.filter(user=request.user)
    if 'del_from_cart' in request.POST:
        try:
            obj = cart_items.get(id=request.POST['del_from_cart'])
            obj.delete()
        except Exception as e:
            pass
    elif 'chg_qty' in request.POST:
        try:
            obj = cart_items.get(id=request.POST['pid'])
            if request.POST['chg_qty'] == '1':
                obj.quantity += 1
            else:
                obj.quantity -= 1
            obj.save()
            if obj.quantity == 0:
                obj.delete()
        except Exception as e:
            pass
    if 'check_out' in request.POST:
        this_order = models.Order(user=request.user, oid='ORDID'+timezone.now().strftime('%Y%m%d%H%M%S')+str(request.user.id))
        this_order.save()
        total = 0
        for item in cart_items:
            prod = models.ProductList(order=this_order, product=item.product, quantity=item.quantity, price=item.product.discounted_price)
            prod.save()
            item.delete()
            total += prod.product.discounted_price * prod.quantity
        this_order.total = total
        this_order.save()
        return redirect('/add_address/'+this_order.oid+'/')
    cart_total = 0
    for item in cart_items:
        cart_total += item.product.discounted_price * item.quantity
    else:
        grand_total = cart_total
    return render(request, 'cart.html',
                  {'cart_items': cart_items,
                   'grand_total': grand_total},
                  status=200)


@login_required
def add_address_view(request, oid):
    try:
        cur_address = models.Address.objects.get(user=request.user)
    except models.Address.DoesNotExist:
        cur_address = models.Address(user=request.user)
        cur_address.save()
    if 'submit' in request.POST:
        cur_address.name = request.POST['name']
        cur_address.phone = request.POST['phone']
        cur_address.address = request.POST['address']
        cur_address.city = request.POST['city']
        cur_address.state = request.POST['state']
        cur_address.pin_code = request.POST['pin_code']
        cur_address.save()

        try:
            this_order = models.Order.objects.get(oid=oid)
            this_order.name = cur_address.name
            this_order.address = cur_address.address
            this_order.city = cur_address.city
            this_order.state = cur_address.state
            this_order.pin_code = cur_address.pin_code
            this_order.phone = cur_address.phone
            this_order.save()

            params = (
                ('MID', MID),
                ('ORDER_ID', this_order.oid),
                ('CUST_ID', str(this_order.user.id)),
                ('TXN_AMOUNT', str(this_order.total)),
                ('CHANNEL_ID', CHANNEL_ID),
                ('WEBSITE', WEBSITE),
                # ('EMAIL', request.user.email),
                # ('MOBILE_N0', '9911223388'),
                ('INDUSTRY_TYPE_ID', INDUSTRY_TYPE),
                ('CALLBACK_URL', 'http://127.0.0.1:8000/after_order_view/'),
                # ('PAYMENT_MODE_ONLY', 'NO'),
            )

            paytm_params = dict(params)
            checksum = generate_checksum(paytm_params, MKEY)
            paytm_params['CHECKSUMHASH'] = checksum
            return render(request, 'redirect.html', context=paytm_params)
        except models.Order.DoesNotExist:
            return redirect(reverse('index'))
    return render(request, 'address.html', {'cur_address': cur_address})


@csrf_exempt
def after_order_view(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        is_valid_checksum = verify_checksum(paytm_params, MKEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
            if paytm_params['STATUS'] == 'TXN_SUCCESS' and paytm_params['MID'] == MID:
                oid = paytm_params['ORDERID']
                try:
                    this_order = models.Order.objects.get(oid=oid)
                    this_order.payment_status = '2'
                    this_order.save()
                    msg = 'Details : http://127.0.0.1:8000/admin/home/order/{}/change/'.format(this_order.id)
                    send_mail('NEW ORDER', msg, SERVER_MAIL, [INFO_MAIL])
                except models.Order.DoesNotExist:
                    return redirect(reverse('index'))
        else:
            received_data['message'] = "Checksum Mismatched"
            return redirect(reverse('orders'))
    return redirect(reverse('orders'))


@login_required
def all_order_view(request):
    orders = models.Order.objects.filter(user=request.user)
    if 'cancel_ord' in request.POST:
        try:
            this_ord = orders.get(oid=request.POST['oid'])
            this_ord.status = '5'
            this_ord.save()
            msg = 'Details : http://127.0.0.1:8000/admin/home/order/{}/change/'.format(this_ord.id)
            send_mail('ORDER CANCEL', msg, SERVER_MAIL, [INFO_MAIL])
        except Exception as e:
            return redirect(reverse('orders'))
    elif 'return_ord' in request.POST:
        try:
            this_ord = orders.get(oid=request.POST['oid'])
            this_ord.status = '6'
            this_ord.save()
            msg = 'Details : http://127.0.0.1:8000/admin/home/order/{}/change/'.format(this_ord.id)
            send_mail('REQUESTED FOR RETURN', msg, SERVER_MAIL, [INFO_MAIL])
        except Exception as e:
            return redirect(reverse('orders'))
    return render(request, 'my_orders.html', {'orders': orders}, status=200)


def forgot_password(request):
    wrong = 0
    email = ''
    if 'send_otp' in request.POST:
        try:
            user = User.objects.get(email=request.POST['email'].strip())
            otp = str(random.randint(100000, 999999))
            email = user.email
            msg = 'OTP : '+otp
            try:
                obj = models.ForgotPassword.objects.get(user=user)
            except models.ForgotPassword.DoesNotExist:
                obj = models.ForgotPassword(user=user)
            obj.otp = otp
            obj.save()
            send_mail('Reset Password', msg, SERVER_MAIL, [email])
        except User.DoesNotExist:
            wrong = 1
    elif 'reset_password' in request.POST:
        try:
            obj = models.ForgotPassword.objects.get(user__email=request.POST['email'], otp=request.POST['otp'])
            user = User.objects.get(email=obj.user.email)
            user.set_password(request.POST['password'])
            user.save()
            obj.delete()
            login(request, user)

            return redirect(reverse('index'))
        except Exception as e:
            wrong = 2
    return render(request, 'forgot.html', {'wrong': wrong, 'email': email}, status=200)