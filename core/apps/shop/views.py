from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import CategorySerializer, ProductSerializer, CreateProductSerializer
from .models import Category, Product
from ..sellers.models import Seller


shop_tag = ['Shop']


class CategoriesView(APIView):
    serializer_class = CategorySerializer

    @extend_schema(
        summary="Categories Fetch",
        description="""This endpoint returns all categories.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Category Creating",
        description="""This endpoint creates categories.""",
        tags=shop_tag
    )
    def post(self, request, *args, **kwargs):
        data_serializer = self.serializer_class(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        category = Category.objects.create(**data_serializer.validated_data)
        serializer = self.serializer_class(category)
        return Response(data=serializer.data)


class DeleteCategoryView(APIView):
    @extend_schema(
        operation_id='delete_category',
        summary="Category Deleting",
        description="""This endpoint deletes categories.""",
        tags=shop_tag
    )
    def delete(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(name=kwargs['cat_slug'])
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        category.delete()
        return Response(data={"message": "Category deleted successfully"}, status=200)


class ListProductView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="all_products",
        summary="Product Fetch",
        description="""This endpoint returns all products.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related('category', 'seller__user').all()
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductByCategoryView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="category_products",
        summary="Category Products Fetch",
        description="""This endpoint returns all products in a particular category.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(slug=kwargs['cat_slug'])
        print(category)
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        products = Product.objects.select_related('category', 'seller', 'seller__user').filter(category=category)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductBySellerView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="seller_products",
        summary="Seller's Products Fetch",
        description="""This endpoint returns all products of a seller.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get_or_none(slug=kwargs['seller_slug'])
        if not seller:
            return Response(data={"message": "Seller does not exist!"}, status=404)
        products = Product.objects.select_related('category', 'seller__user').filter(seller=seller)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="product_detail",
        summary="Product Details Fetch",
        description="""This endpoint returns the details for a product via the slug.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        product = Product.objects.select_related('category', 'seller__user').get_or_none(slug=kwargs['prod_slug'])
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        serializer = self.serializer_class(instance=product)
        return Response(data=serializer.data, status=200)
