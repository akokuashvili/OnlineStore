from rest_framework import serializers

from ..common.utils import UpdateMixin


class ProfileSerializer(UpdateMixin, serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(read_only=True)
    avatar = serializers.ImageField(required=False)
    account_type = serializers.CharField(read_only=True)


class ShippingAddressSerializer(UpdateMixin, serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    zipcode = serializers.CharField(max_length=6)


