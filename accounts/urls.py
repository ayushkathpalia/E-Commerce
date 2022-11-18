from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),  
    path('dashboard/',views.dashboard,name="dashboard"),
    path('',views.dashboard,name="dashboard"),
    path('forgotpassword/',views.forgotpassword,name="forgotpassword"),
    path('resetpassword/',views.resetpassword,name="resetpassword"),
    path('my_orders/',views.my_orders,name="my-orders"),
    path('edit_profile/',views.edit_profile,name="edit-profile"),
    path('change_password/',views.change_password,name="change-password"),
     path('order_detail/<int:order_id>',views.order_detail,name="order-detail"),
    #email functions
    path('activate/<uidb64>/<token>',views.activate,name="activate"), 
    path('resetpassword_validate/<uidb64>/<token>',views.resetpassword_validate,name="resetpassword_validate"), 
]