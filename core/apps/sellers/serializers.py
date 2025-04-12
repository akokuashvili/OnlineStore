from rest_framework import serializers

from ..common.utils import UpdateMixin


class SellerSerializer(UpdateMixin, serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    slug = serializers.CharField(read_only=True)
    inn_number = serializers.CharField(max_length=50)
    website_url = serializers.URLField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20)
    business_description = serializers.CharField()

    business_address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)

    bank_name = serializers.CharField(max_length=255)
    bic_bank_number = serializers.CharField(max_length=9)
    bank_account_number = serializers.CharField(max_length=50)
    bank_routing_number = serializers.CharField(max_length=50)

    is_approved = serializers.BooleanField(read_only=True)