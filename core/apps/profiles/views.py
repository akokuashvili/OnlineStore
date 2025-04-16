from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import ProfileSerializer, ShippingAddressSerializer
from ..shop.serializers import OrderSerializer, CheckItemOrderSerializer
from .models import ShippingAddress, Order, OrderItem


profile_tag = ['Profiles']
shipping_tag = ['Profile Shipping Addresses']
order_tag = ['Profile Orders']


class ProfileView(APIView):
    serializer_class = ProfileSerializer

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

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description="""This endpoint returns all shipping addresses associated with a user.""",
        tags=shipping_tag,
    )
    def get(self, request, *args, **kwargs):
        shipping_addresses = ShippingAddress.objects.filter(user=request.user)
        serializer = self.serializer_class(shipping_addresses, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Create Shipping Address",
        description="""This endpoint allows a user to create a shipping address.""",
        tags=shipping_tag,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, created = ShippingAddress.objects.get_or_create(user=request.user, **data)
        status = 201 if created else 200
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=status)


class ShippingAddressViewID(APIView):
    serializer_class = ShippingAddressSerializer

    def get_object(self, user, shipping_id):
        address = ShippingAddress.objects.get_or_none(user=user, id=shipping_id)
        return address

    @extend_schema(
        summary="Shipping Address Fetch ID",
        description="""This endpoint returns a single shipping address associated with a user.""",
        tags=shipping_tag,
    )
    def get(self, request, **kwargs):
        user = request.user
        address = self.get_object(user, kwargs['id'])
        if not address:
            return Response({"message": "Shipping address doesn't exist"}, status=404)
        serializer = self.serializer_class(instance=address)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Update Shipping Address ID",
        description="""This endpoint allows a user to update shipping address.""",
        tags=shipping_tag,
    )
    def put(self, request, partial=False, **kwargs):
        address = self.get_object(request.user, kwargs['id'])
        if not address:
            return Response({"message": "Shipping address doesn't exist"}, status=404)
        serializer = self.serializer_class(address, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Partial Update Shipping Address ID",
        description="""This endpoint allows a user to partial update shipping address.""",
        tags=shipping_tag,
    )
    def patch(self, request, **kwargs):
        return self.put(request, partial=True, **kwargs)

    @extend_schema(
        summary="Delete Shipping Address ID",
        description="""This endpoint allows a user to delete shipping address.""",
        tags=shipping_tag,
    )
    def delete(self, request, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        if not shipping_address:
            return Response(data={"message": "Shipping Address does not exist!"}, status=404)
        shipping_address.delete()
        return Response(data={"message": "Shipping address deleted successfully"}, status=200)


class OrdersView(APIView):
    serializer_class = OrderSerializer

    @extend_schema(
        operation_id="orders_view",
        summary="Orders Fetch",
        description="""This endpoint returns all orders for a particular user.""",
        tags=order_tag
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related('user')\
            .prefetch_related("order_items__product").order_by("-created_at")

        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data, status=200)


class OrderItemsView(APIView):
    serializer_class = CheckItemOrderSerializer

    @extend_schema(
        operation_id="order_items_view",
        summary="Items Order Fetch",
        description="""This endpoint returns all items order for a particular user.""",
        tags=order_tag,
    )
    def get(self, request, **kwargs):
        order = Order.objects.filter(user=request.user).get_or_none(tx_ref=kwargs["tx_ref"])
        if not order:
            return Response(data={"message": "Order does not exist!"}, status=404)
        order_items = OrderItem.objects.filter(order=order).\
            select_related('product__seller__user', 'product__category')
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)
