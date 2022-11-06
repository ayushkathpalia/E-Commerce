from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.views import CartItem,_cart_id
from django.db.models import Q
# Create your views here.

from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage

def store(request,category_slug=None):
    products = None
    categories = None
    if category_slug:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category = categories,is_available=True)
        products_count = products.count()
        paginator = Paginator(products,1)
        page = request.GET.get('page')
        pagged_products = paginator.get_page(page)
    else:
        products = Product.objects.all().filter(is_available=True)
        products_count = products.count()
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        pagged_products = paginator.get_page(page)
        
    context = {
        'products':pagged_products,
        'products_count':products_count
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug,slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart
    }
    return render(request,'store/product_detail.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            products_count = products.count()
    context = {
        'products' : products,
        'products_count' : products_count
    }
    print(context)
    return render(request,'store/store.html',context)