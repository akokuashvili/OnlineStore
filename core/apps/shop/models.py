from django.db import models
from autoslug import AutoSlugField

from ..common.models import BaseModel, IsDeletedModel
from ..sellers.models import Seller


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique_with='name', always_update=True)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(IsDeletedModel):
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, related_name='products', null=True)
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name', unique=True, db_index=True)
    description = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    in_stock = models.IntegerField(default=5)

    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True)

    def __str__(self):
        return self.name
