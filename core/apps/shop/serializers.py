from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from ..common.utils import UpdateMixin
from ..sellers.serializers import SellerSerializer
from ..profiles.serializers import ShippingAddressSerializer
from ..common.serializers import DymanicFieldSerializer
from .models import Review, Category


class CategorySerializer(serializers.ModelSerializer):
    # name = serializers.CharField()
    # slug = serializers.SlugField(read_only=True)
    # image = serializers.ImageField(required=False)
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image']
        read_only_fields = ['slug']
        extra_kwargs = {
            'name': {'required': True},
            'image': {'required': False}
        }


class SellerShopSerializer(serializers.Serializer):
    name = serializers.CharField(source="business_name")
    slug = serializers.CharField()
    avatar = serializers.CharField(source="user.avatar")


class ProductSerializer(DymanicFieldSerializer):
    seller = SellerShopSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    description = serializers.CharField()
    price_old = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    in_stock = serializers.IntegerField()
    reviews = serializers.IntegerField(source='get_reviews_count')
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, source="get_rating")
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


class CreateProductSerializer(UpdateMixin, serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_slug = serializers.CharField()
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


# Используется для представления информации о продукте внутри элемента заказа
class OrderItemProductSerializer(serializers.Serializer):
    seller = SellerSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source="price_current")


# Используется для представления всего элемента заказа
class OrderItemSerializer(serializers.Serializer):
    product = OrderItemProductSerializer()
    quantity = serializers.IntegerField(default=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, source="get_total")


# Используется для валидации данных, отправленных клиентом при добавлении,
# обновлении или удалении товара из корзины.
class ToggleCartItemSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    quantity = serializers.IntegerField(min_value=0)


class CheckoutSerializer(serializers.Serializer):
    shipping_id = serializers.UUIDField()


class OrderSerializer(serializers.Serializer):
    tx_ref = serializers.CharField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    delivery_status = serializers.CharField()
    payment_status = serializers.CharField()
    date_delivered = serializers.DateTimeField()
    shipping_details = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=100, decimal_places=2, source="get_cart_subtotal")
    total = serializers.DecimalField(max_digits=100, decimal_places=2, source="get_cart_total")

    @extend_schema_field(ShippingAddressSerializer)
    def get_shipping_details(self, obj):
        return ShippingAddressSerializer(obj).data


class CheckItemOrderSerializer(serializers.Serializer):
    product = ProductSerializer(exclude_fields=['in_stock'])
    quantity = serializers.IntegerField()
    total = serializers.FloatField(source="get_total")


class ReviewSerializer(UpdateMixin, DymanicFieldSerializer):
    full_name = serializers.CharField(source='user.full_name')
    product = ProductSerializer(exclude_fields=['in_stock', 'seller', 'category', 'price_old'])
    rating = serializers.IntegerField()
    text = serializers.CharField(max_length=None)


class CreateReviewSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=Review.RATING_CHOICES)
    text = serializers.CharField(max_length=None)
