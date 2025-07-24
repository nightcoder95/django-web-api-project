from django.db import models
from apps.users.models import User
from apps.products.models import Product
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings
import base64
import json

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    encrypted_data = models.TextField()  # AES encrypted order details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def encrypt_order_data(self, data):
        """Encrypt order data using AES"""
        key = settings.AES_SECRET_KEY.encode('utf-8')
        iv = settings.AES_SECRET_IV.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        json_data = json.dumps(data)
        encrypted = cipher.encrypt(pad(json_data.encode(), 16))
        self.encrypted_data = base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_order_data(self):
        """Decrypt order data using AES"""
        key = settings.AES_SECRET_KEY.encode('utf-8')
        iv = settings.AES_SECRET_IV.encode('utf-8')
        encrypted_bytes = base64.b64decode(self.encrypted_data)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_bytes), 16)
        return json.loads(decrypted.decode('utf-8'))

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
