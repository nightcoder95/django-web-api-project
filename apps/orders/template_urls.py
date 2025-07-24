from django.urls import path
from .template_views import (
    CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView,
    CheckoutView, OrderListView, OrderDetailView, CartCountView
)

urlpatterns = [
    # Cart URLs
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/count/', CartCountView.as_view(), name='cart_count'),
    
    # Order URLs
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
]
