from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from carts.models import CartItem
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import random
#paytm 
from . import paytm_api 
import paytmchecksum

def place_order(request,total = 0,quantity=0):
    current_user = request.user

    #check if cart items are present
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total +=(cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total+tax


    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #Generate Order Number
            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            date = int(datetime.date.today().strftime('%d'))
            d = datetime.date(year,month,date)
            current_date = d.strftime("%Y%m%d")
            order_number =  current_date+str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number = order_number)
            request.session['order_number'] = order_number
            request.session.save()
            print(f'OrderNO_SESSION:{order_number}')
            #paytm getToken
            #token = paytm_api.getTransactionToken(grand_total,order_number)
            #print(f'TOKEN:{token}')
            context = {
                'order' : order,
                'cart_items':cart_items,
                'total' : total,
                'grand_total':grand_total,
                'tax':tax,
                'order_id':order_number,
                'token':'123456790'
            }
            return render(request,'orders/payments.html',context)
        else:
            print(form.errors.as_data())
    else:
        return redirect('checkout')

def payments(request):

    #check the response of payment
    #check the response of validate api
    # result = paytm_api.transactionStatus('20221116164')
    status = '01'
    
    #Generate Transaction ID - Temporary
    payment_id = random.randrange(10000000)
    print(f'PAYMENT_ID: {payment_id}')

    #Payment Successful
    if status == '01':
        order_id = request.session['order_number'] 
        order = Order.objects.get(user = request.user,is_ordered=False,order_number=order_id)
        payment = Payment(
            user = request.user,
            payment_id = payment_id, #change later
            payment_method = 'Paytm',
            amount_paid = order.order_total,
            status = 'Success'
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        #Move Cart Items to Order Product Table
        cart_items = CartItem.objects.filter(user = request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id = item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id = orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

        #Reduce the quantity of Sold product
            product = Product.objects.get(id = item.product_id)
            product.stock -= item.quantity
            product.save()

        #Clear Cart
        CartItem.objects.filter(user=request.user).delete()

        #Order Successful E-Mail
        mail_subject = 'Thank You For your Order!'
        message = render_to_string('orders/order_successful_email.html',{
            'user':request.user,
            'order':order
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject,message,to=[to_email])
        send_email.send()
        request.session['transId'] = payment_id
        request.session.save()
        return redirect('order_complete')
    
    #payment unsuccessful due to any reason
    else:
        order_id = request.session['order_number'] 
        order = Order.objects.get(user = request.user,is_ordered=False,order_number=order_id)
        payment = Payment(
            user = request.user,
            payment_id = payment_id, #change later
            payment_method = 'Paytm',
            amount_paid = order.order_total,
            status = 'Failed('+status+')'
        )
        payment.save()
        order.payment = payment
        order.is_ordered = False
        order.save()
        return redirect('order_failed')

def order_complete(request):
    order_id = request.session['order_number'] 
    trans_id = request.session['transId'] 

    try :
        order = Order.objects.get(order_number = order_id,is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id = trans_id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order':order,
            'ordered_products' : ordered_products,
            'trans_id' : payment.payment_id,
            'order_id' :order.order_number,
            'payment':payment,
            'subtotal':subtotal
        }
        print(context)
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')

def order_failed(request):
    return render(request,'orders/order_failed.html')




# @csrf_exempt
# def app_callback(request):
#     data = (request.POST).dict()
#     print(f'DATA:{data}')
#     text_success = ''
#     verifySignature = ''
#     if data:
#          checksum = data['CHECKSUMHASH']
#          data.pop('CHECKSUMHASH', None)

#          #verify checksum
#          verifySignature = paytmchecksum.verifySignature(data, paytm_api.PAYTM_MERCHANT_KEY, checksum)
#          text_error = ''

#          if verifySignature:
#            text_success = "Checksum is verified.Transaction details are below"
#          else:
#           text_error = "Checksum is not verified."
#     else :
#      text_error = "Empty POST Response."
#     context = {
#         'data' : data,
#         'text_success': text_success,
#         'text_error':text_error,
#         'verifySignature' : verifySignature
#     }
#     return HttpResponse(context)
#     # return render(request,'orders/callback.html',context)