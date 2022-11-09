from math import prod
from django.http import HttpResponse
from django.shortcuts import render,redirect
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variations
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.
def cart(request,total = 0,quantity = 0 ,cart_items = None,tax = 0,grand_total=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user = request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (2*total)/100
            grand_total = total+tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/cart.html',context)

def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user = request.user,product=product,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user = request.user,product=product,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

#private method to get session key / create session key
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
       cart = request.session.create()
    return cart

def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variations.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        is_cart_items_exists = CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_items_exists:
        #Items of Cart
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                # cart_item.quantity +=1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    else:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variations.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        #Cart
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get cart items using the session key of user
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)    #creating session key, 1st time user
            )
            cart.save()

        is_cart_items_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_items_exists:
        #Items of Cart
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                # cart_item.quantity +=1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

@login_required(login_url="login")
def checkout(request,total = 0,quantity = 0 ,cart_items = None,tax = 0,grand_total=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user = request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (2*total)/100
            grand_total = total+tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/checkout.html',context)