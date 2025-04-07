from rest_framework import serializers

from ..accounts.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'account_type')
        read_only_fields = ('email', 'account_type')