from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from orders.models import Order,OrderProduct
# Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes

import requests

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name = first_name,last_name = last_name,username = username,email = email,password = password)
            user.save()

            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-image2.png'
            profile.save()

            #USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Please Activate your Account !'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            
            #messages.success(request,'Registration Successful! Start Shopping!')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_items_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_items_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    #getting product variation through cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #get cart item from user to access the product variations
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request,user)
            messages.success(request,'You are Logged In.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request,'Bad Credentials.Please Try Again')
            return redirect('login')

    return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are Logged Out.')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Your Account is Active')
        return redirect('login')
    else:
        messages.error(request,'Link has been Expired')
        return redirect('register')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please Reset your Password')
        return redirect('resetpassword')
    else:
        messages.error(request,'Link has been Expired.')
        return redirect('login')

def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password Reset Successful')
            return redirect('login')
        else:
            messages.error(request,'Password Does not Match!')
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    orders_count = orders.count()
    context = {
        'order_count':orders_count,
        'userprofile' : userprofile
    }
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user_id=request.user.id,is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order' : order,
        'subtotal':subtotal
    }
    return render(request,'accounts/order_detail.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your Profile has been Updated")
            return redirect('edit-profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form' : user_form,
        'profile_form':profile_form,
        'userprofile':userprofile
    }
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password Changed Succesful')
                return redirect('change-password')
            else:
                messages.error(request,'Please enter a Valid Current Password')
                return redirect('change-password')
        else:
            messages.error(request,'Password Does not Match')
            return redirect('change-password')
    return render(request,'accounts/change_password.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Please Reset your Password !'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Password Reset Email has been sent to your Email')
            return redirect('login')
        else:
            messages.error(request,'Account Does not Exisits!')
            return redirect('forgotpassword')

    return render(request,'accounts/forgotpassword.html')