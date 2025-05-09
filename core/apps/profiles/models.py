from django.db import models

from ..common.models import BaseModel, IsDeletedModel
from ..accounts.models import User
from ..common.utils import generate_unique_code
from ..shop.models import Product


class ShippingAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=6, null=True)

    def __str__(self):
        return f"{self.full_name}'s shipping details"


DELIVERY_STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("PACKING", "PACKING"),
    ("SHIPPING", "SHIPPING"),
    ("ARRIVING", "ARRIVING"),
    ("SUCCESS", "SUCCESS"),
)

PAYMENT_STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("PROCESSING", "PROCESSING"),
    ("SUCCESSFUL", "SUCCESSFUL"),
    ("CANCELLED", "CANCELLED"),
    ("FAILED", "FAILED"),
)


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    tx_ref = models.CharField(max_length=100, blank=True, unique=True)
    delivery_status = models.CharField(max_length=20, default="PENDING",
                                       choices=DELIVERY_STATUS_CHOICES)
    payment_status = models.CharField(max_length=20, default="PENDING",
                                      choices=PAYMENT_STATUS_CHOICES)
    date_delivered = models.DateTimeField(null=True, blank=True)

    # Shipping address details
    full_name = models.CharField(max_length=1000, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=6, null=True)

    @property
    def get_cart_subtotal(self):
        order_items = self.order_items.all()
        subtotal = sum(item.get_total for item in order_items)
        return subtotal

    @property
    def get_cart_total(self):
        total = self.get_cart_subtotal
        return total

    def __str__(self):
        return f"{self.user.full_name}'s order"

    def save(self, *args, **kwargs) -> None:
        if not self.created_at:
            self.tx_ref = generate_unique_code(Order, "tx_ref")
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def get_total(self):
        return self.product.price_current * self.quantity

    @property
    def get_in_stock(self):
        return self.product.in_stock

    def __str__(self):
        return self.product.name

    class Meta:
        ordering = ['-created_at']
