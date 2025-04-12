from django.db import models
from autoslug import AutoSlugField

from ..common.models import BaseModel
from ..accounts.models import User


class Seller(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller')

    business_name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='business_name', always_update=True, null=True)
    inn_number = models.CharField(max_length=12)
    website_url = models.URLField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    business_description = models.TextField()

    business_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    bank_name = models.CharField(max_length=127)
    bic_bank_number = models.CharField(max_length=9)
    bank_account_number = models.CharField(max_length=50)
    bank_routing_number = models.CharField(max_length=50)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Seller for {self.business_name}"