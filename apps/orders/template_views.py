from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, View, TemplateView
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse_lazy
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem
from apps.products.models import Product


class CartView(LoginRequiredMixin, TemplateView):
    """Display user's cart"""
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.select_related('product').all()
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
        })
        return context


class AddToCartView(LoginRequiredMixin, View):
    """Add product to cart"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, status='approved')
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.title} quantity in cart.')
        else:
            messages.success(request, f'Added {product.title} to cart.')
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_items,
                'message': 'Product added to cart'
            })
        
        return redirect('cart')


class UpdateCartItemView(LoginRequiredMixin, View):
    """Update cart item quantity"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        
        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove item from cart"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_title = cart_item.product.title
        cart_item.delete()
        messages.success(request, f'Removed {product_title} from cart.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                cart = Cart.objects.get(user=request.user)
                cart_total = cart.total_items
            except Cart.DoesNotExist:
                cart_total = 0
                
            return JsonResponse({
                'success': True,
                'cart_total': cart_total,
                'message': 'Item removed from cart'
            })
        
        return redirect('cart')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout process"""
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_object_or_404(Cart, user=self.request.user)
        cart_items = cart.items.select_related('product').all()
        
        if not cart_items:
            messages.error(self.request, 'Your cart is empty.')
            return context
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related('product').all()
        
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.total_amount,
                status='pending'
            )
            
            # Create order items and encrypt data
            order_data = {
                'order_id': order.id,
                'items': [],
                'customer': {
                    'username': request.user.username,
                    'email': request.user.email,
                }
            }
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                order_data['items'].append({
                    'product_id': cart_item.product.id,
                    'title': cart_item.product.title,
                    'quantity': cart_item.quantity,
                    'price': str(cart_item.product.price),
                    'total': str(cart_item.total_price)
                })
            
            # Encrypt order data
            order.encrypt_order_data(order_data)
            order.save()
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('order_detail', order_id=order.id)


class OrderListView(LoginRequiredMixin, ListView):
    """List user's orders"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Order detail view with AES decryption"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_items = order.items.select_related('product').all()
        
        # Decrypt order data
        try:
            decrypted_data = order.decrypt_order_data()
        except:
            decrypted_data = None
        
        context.update({
            'order_items': order_items,
            'decrypted_data': decrypted_data,
        })
        return context


class CartCountView(LoginRequiredMixin, View):
    """AJAX endpoint to get cart item count"""
    
    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            count = 0
        
        return JsonResponse({'count': count})
