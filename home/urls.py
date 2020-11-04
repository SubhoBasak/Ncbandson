from django.urls import path
from . import views

handler404 = views.handler404

urlpatterns = [
    path('', views.index_view, name='index'),
    path('contact_us/', views.contact_us_view, name='contact_us'),
    path('authentication/', views.authentication, name='auth_url'),
    path('cart/', views.cart_view, name='cart'),
    path('about_us/', views.about_us_view, name='about_us'),
    path('details/<int:pid>/', views.detail_view, name='detail'),
    path('add_to_cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('add_address/<str:oid>/', views.add_address_view, name='add_address'),
    path('my_orders/', views.all_order_view, name='orders'),
    path('after_order_view/', views.after_order_view, name='after_order_view'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]