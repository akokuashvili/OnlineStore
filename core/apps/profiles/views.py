from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import ProfileSerializer, ShippingAddressSerializer
from ..shop.serializers import OrderSerializer, CheckItemOrderSerializer, ReviewSerializer
from .models import ShippingAddress, Order, OrderItem
from ..shop.models import Review, Product
from ..common.permissions import IsOwner
from ..common.paginations import CustomNumberPagination


profile_tag = ['Profiles']
profile_address = ['Profile Shipping Info']


class ProfileView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary="Retrieve Profile",
        description="""This endpoint allows a user to retrieve profile.""",
        tags=profile_tag,
    )
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Update Profile",
        description="""This endpoint allows a user to update profile.""",
        tags=profile_tag,
        # request={"multipart/form-data": serializer_class},
    )
    def put(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @extend_schema(
        summary="Partial Update Profile",
        description="""This endpoint allows a user to partial update profile.""",
        tags=profile_tag,
    )
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @extend_schema(
        summary="Deactivate account",
        description="""This endpoint allows a user to deactivate account.""",
        tags=profile_tag,
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': f'Account {user.email} deactivated'})


class ShippingAddressView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description="""This endpoint returns all shipping addresses associated with a user.""",
        tags=profile_address,
    )
    def get(self, request, *args, **kwargs):
        shipping_addresses = ShippingAddress.objects.filter(user=request.user)
        serializer = self.serializer_class(shipping_addresses, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Create Shipping Address",
        description="""This endpoint allows a user to create a shipping address.""",
        tags=profile_address,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, created = ShippingAddress.objects.get_or_create(user=request.user, **data)
        status = 201 if created else 200
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=status)


class ShippingAddressDetailView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsOwner]

    def get_object(self, shipping_id):
        address = ShippingAddress.objects.get_or_none(id=shipping_id)
        if address:
            self.check_object_permissions(self.request, address)
        return address

    @extend_schema(
        summary="Shipping Address Fetch ID",
        description="""This endpoint returns a single shipping address associated with a user.""",
        tags=profile_address,
    )
    def get(self, request, *args, **kwargs):
        address = self.get_object(kwargs['id'])
        if not address:
            return Response({"message": "Shipping address doesn't exist"}, status=404)
        serializer = self.serializer_class(instance=address)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Update Shipping Address ID",
        description="""This endpoint allows a user to update shipping address.""",
        tags=profile_address,
    )
    def put(self, request, partial=False, **kwargs):
        address = self.get_object(kwargs['id'])
        if not address:
            return Response({"message": "Shipping address doesn't exist"}, status=404)
        serializer = self.serializer_class(address, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Partial Update Shipping Address ID",
        description="""This endpoint allows a user to partial update shipping address.""",
        tags=profile_address,
    )
    def patch(self, request, **kwargs):
        return self.put(request, partial=True, **kwargs)

    @extend_schema(
        summary="Delete Shipping Address ID",
        description="""This endpoint allows a user to delete shipping address.""",
        tags=profile_address,
    )
    def delete(self, request, **kwargs):
        shipping_address = self.get_object(kwargs["id"])
        if not shipping_address:
            return Response(data={"message": "Shipping Address does not exist!"}, status=404)
        shipping_address.delete()
        return Response(data={"message": "Shipping address deleted successfully"}, status=200)


class OrdersView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        operation_id="orders_view",
        summary="Orders Fetch",
        description="""This endpoint returns all orders for a particular user.""",
        tags=profile_tag
    )
    def get(self, request):
        orders = Order.objects.select_related('user').filter(user=request.user)\
            .prefetch_related("order_items__product").order_by("-created_at")
        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data, status=200)


class OrderItemsView(APIView):
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsOwner]

    def get_object(self, **kwargs):
        order = Order.objects.get_or_none(tx_ref=kwargs["tx_ref"])
        if order:
            self.check_object_permissions(self.request, order)
        return order

    @extend_schema(
        operation_id="order_items_view",
        summary="Items Order Fetch",
        description="""This endpoint returns all items order for a particular user.""",
        tags=profile_tag,
    )
    def get(self, request, *args, **kwargs):
        order = self.get_object(**kwargs)
        if not order:
            return Response(data={"message": "Order does not exist!"}, status=404)
        order_items = OrderItem.objects.filter(order=order).\
            select_related('product__seller__user', 'product__category')
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)


@extend_schema_view(
    get=extend_schema(
        operation_id="reviews_fetch",
        summary="Fetch all your reviews",
        description="""This endpoint returns all your reviews.""",
        tags=profile_tag,
    )
)
class ReviewsListView(ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwner]
    pagination_class = CustomNumberPagination

    def get(self, request, *args, **kwargs):
        reviews = self.request.user.reviews.select_related('product')
        # reviews = Review.objects.select_related('user', 'product').filter(user=request.user)
        serializer = self.serializer_class(reviews, many=True, exclude_fields=['full_name'])
        return Response(data={'full_name': request.user.full_name,
                              'reviews': serializer.data}, status=200)

