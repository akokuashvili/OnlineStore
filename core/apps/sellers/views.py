from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import SellerSerializer
from .models import Seller
from ..shop.serializers import ProductSerializer, CreateProductSerializer
from ..shop.models import Product, Category


seller_tag = ['Sellers']

seller_doesnt_exist_message = {
    'message': "Your account type is 'BUYER'. You need to become a 'seller' to retrieve seller's info"
}


class SellerView(APIView):
    serializer_class = SellerSerializer

    def get_object(self, request):
        seller = Seller.objects.get_or_none(user=request.user)
        return seller

    @extend_schema(
        summary="Apply to become a seller",
        description="""This endpoint allows a buyer to apply to become a seller.""",
        tags=seller_tag
    )
    def post(self, request):
        user = request.user
        data_serializer = self.serializer_class(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        data = data_serializer.validated_data
        seller, _ = Seller.objects.update_or_create(user=user, defaults=data)
        user.account_type = 'SELLER'
        user.save()
        serializer = self.serializer_class(seller)
        return Response(data=serializer.data, status=201)

    @extend_schema(
        summary="Retrieve Seller's info",
        description="""This endpoint allows a seller to retrieve his info.""",
        tags=seller_tag
    )
    def get(self, request):
        seller = self.get_object(request)
        if not seller:
            return Response(seller_doesnt_exist_message)
        serializer = self.serializer_class(instance=seller)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Partial Update Seller's info",
        description="""This endpoint allows a seller to partial update his info.""",
        tags=seller_tag
    )
    def patch(self, request):
        seller = self.get_object(request.user)
        if not seller:
            return Response(seller_doesnt_exist_message)
        serializer = self.serializer_class(seller, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)


class SellerProductsView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        summary="Seller Products Fetch",
        description="""This endpoint returns all products from a seller.
                        Products can be filtered by name, sizes or colors.""",
        tags=seller_tag,
    )
    def get(self, request):
        seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not seller:
            return Response(data={"message": "Access is denied"}, status=403)
        products = Product.objects.select_related('category', 'seller', 'seller__user').filter(seller=seller)
        serializer = self.serializer_class(instance=products, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Create a product",
        description="""This endpoint allows a seller to create a product.""",
        tags=seller_tag,
        request=CreateProductSerializer,
        responses=CreateProductSerializer,
    )
    def post(self, request):
        seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not seller:
            return Response(data={"message": "Access is denied"}, status=403)
        data_serializer = CreateProductSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        data = data_serializer.validated_data
        category_slug = data.pop('category_slug', None)
        category = Category.objects.get_or_none(slug=category_slug)
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        product = Product.objects.create(seller=seller, category=category, **data)
        serializer = self.serializer_class(instance=product)
        return Response(data=serializer.data, status=201)


class SellerProductView(APIView):
    serializer_class = CreateProductSerializer

    @extend_schema(
        summary="Update a product",
        description="""This endpoint allows a seller to update a product.""",
        tags=seller_tag,
        request=CreateProductSerializer,
        responses=CreateProductSerializer,
    )
    def put(self, request, slug):
        product = Product.objects.select_related('seller__user').get_or_none(slug=slug)
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        if request.user != product.seller.user:
            return Response(data={"message": "Access is denied"}, status=403)
        old_price = product.price_current
        serializer = self.serializer_class(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        category_slug = serializer.validated_data.get('category_slug', None)
        category = Category.objects.get_or_none(slug=category_slug)
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        serializer.save()
        if serializer.data['price_current'] != old_price:
            product.price_old = old_price
            product.save()
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Delete a product",
        description="""This endpoint allows a seller to delete a product.""",
        tags=seller_tag,
    )
    def delete(self, request, slug):
        product = Product.objects.select_related('seller__user').get_or_none(slug=slug)
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        if request.user != product.seller.user:
            return Response(data={"message": "Access is denied"}, status=403)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=204)