from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers
from .models import Category, Product, Review
from ..sellers.models import Seller
from ..profiles.models import Order, OrderItem, ShippingAddress
from .filters import ProductFilter, ReviewFilter
from ..common.permissions import IsOwner, IsStaff
from ..common.paginations import CustomNumberPagination
from .schema_examples import PRODUCT_PARAMS, REVIEWS_PARAMS

shop_tag = ['Shop']
cart_checkout_tag = ['Cart & Checkout']


@extend_schema_view(
    list=extend_schema(
        summary="Categories Fetch",
        description="""This endpoint returns all categories.""",
        tags=shop_tag
    ),
    create=extend_schema(
        summary="Create a Category",
        description="""This endpoint creates category. Only for staff""",
        tags=shop_tag
    ),
    update=extend_schema(
        summary="Update a Category",
        description="""This endpoint updates category. Only for staff""",
        tags=shop_tag
    ),
    destroy=extend_schema(
        summary="Delete a Category",
        description="""This endpoint deletes category. Only for staff""",
        tags=shop_tag
    )
)
class CategoriesView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsStaff]
    lookup_field = 'slug'
    lookup_url_kwarg = 'cat_slug'


@extend_schema_view(
    get=extend_schema(
        operation_id="all_products",
        summary="All Products Fetch",
        description="""This endpoint returns all products.""",
        tags=shop_tag,
        parameters=PRODUCT_PARAMS,
    )
)
class ListProductView(ListAPIView):
    queryset = Product.objects.select_related("category", "seller__user").prefetch_related('reviews')
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomNumberPagination


class ProductByCategoryView(APIView):
    serializer_class = serializers.ProductSerializer

    @extend_schema(
        operation_id="category_products",
        summary="Products Fetch by Category",
        description="""This endpoint returns all products in a particular category.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(slug=kwargs['cat_slug'])
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        products = Product.objects.select_related('category', 'seller__user').filter(category=category)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


@extend_schema_view(
    get=extend_schema(
        operation_id="seller_products",
        summary="Products Fetch by Seller",
        description="""This endpoint returns all products of a seller.""",
        tags=shop_tag,
        parameters=PRODUCT_PARAMS
    )
)
class ProductBySellerView(ListAPIView):
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomNumberPagination

    def get_queryset(self):
        seller = Seller.objects.get_or_none(slug=self.kwargs.get('seller_slug'))
        if not seller:
            raise ValidationError("Seller doesn't exist")
        return Product.objects.select_related('category', 'seller__user').filter(seller=seller)


class ProductView(APIView):
    serializer_class = serializers.ProductSerializer

    @extend_schema(
        operation_id="product_detail",
        summary="Product Details Fetch",
        description="""This endpoint returns the details for a product via the slug.""",
        tags=shop_tag
    )
    def get(self, request, *args, **kwargs):
        product = Product.objects.select_related('category', 'seller__user').get_or_none(slug=kwargs['prod_slug'])
        if not product:
            raise ValidationError("Seller doesn't exist")
        serializer = self.serializer_class(instance=product)
        return Response(data=serializer.data, status=200)


class CartView(APIView):
    serializer_class = serializers.OrderItemSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary="Cart Items Fetch",
        description="""This endpoint returns all items in a user cart.""",
        tags=cart_checkout_tag,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        order_items = OrderItem.objects.filter(user=user, order=None).select_related("product__seller__user")
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Toggle Item in cart",
        description="""This endpoint allows a user or guest to add/update/remove an item in cart.
                        If quantity is 0, the item is removed from cart""",
        tags=cart_checkout_tag,
        request=serializers.ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = serializers.ToggleCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data["quantity"]
        product = Product.objects.select_related("seller__user").get_or_none(slug=data["slug"])
        if not product:
            return Response({"message": "No Product with that slug"}, status=404)
        if quantity > product.in_stock:
            return Response({"message": f"There is only {product.in_stock} of {product.name} in stock"}, status=400)
        order_item, created = OrderItem.objects.update_or_create(
            user=user,
            order_id=None,
            product=product,
            defaults={"quantity": quantity},
        )
        resp_message_substring = "Updated In"
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = "Added To"
        if order_item.quantity == 0:
            resp_message_substring = "Removed From"
            order_item.delete()
            data = None
        if resp_message_substring != "Removed From":
            serializer = self.serializer_class(order_item)
            data = serializer.data
        return Response(data={"message": f"Item {resp_message_substring} Cart", "item": data}, status=status_code)


class CheckoutView(APIView):
    serializer_class = serializers.CheckoutSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary="Checkout",
        description="""This endpoint allows a user to create an order through which payment can then be made through.""",
        tags=cart_checkout_tag,
        request=serializers.CheckoutSerializer,
    )
    def post(self, request):
        # Proceed to checkout
        user = request.user
        order_items = OrderItem.objects.select_related('product').filter(user=user, order=None)
        if not order_items.exists():
            return Response({"message": "No Items in Cart"}, status=404)
        quantity_validate_dct = {}
        for item in order_items:
            if item.quantity > item.get_in_stock:
                quantity_validate_dct[item.product.name] = item.get_in_stock
        if quantity_validate_dct:
            message = 'Please reduce the amount of the following products:\n' + \
                      '\n'.join(f'{k} in stock - {v}' for k, v in quantity_validate_dct.items())
            return Response({"message": message}, status=400)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipping_id = serializer.validated_data.get("shipping_id")
        if shipping_id:
            address = ShippingAddress.objects.get_or_none(id=shipping_id)
            if not address:
                return Response({"message": "No shipping address with that ID"}, status=404)
        fields_to_update = ["full_name", "email", "phone", "address", "city", "country", "zipcode"]
        data = {}
        for field in fields_to_update:
            value = getattr(address, field)
            data[field] = value
        order = Order.objects.create(user=user, **data)
        for item in order_items:
            item.product.in_stock -= item.quantity
            item.product.save()
        order_items.update(order=order)
        serializer = serializers.OrderSerializer(order)
        return Response(data={"message": "Checkout Successful", "item": serializer.data}, status=200)


@extend_schema_view(
    post=extend_schema(
        operation_id="review_create",
        summary="Create or Update Product review",
        description="""This endpoint allows you to create/update a product review.
                        Rate it from 1 to 5""",
        tags=shop_tag,
    ),
    get=extend_schema(
        operation_id="reviews_retrieve",
        summary="Product Reviews Fetch",
        description="""This endpoint returns all product reviews.""",
        tags=shop_tag,
        parameters=REVIEWS_PARAMS
    ),
    delete=extend_schema(
        operation_id="review_delete",
        summary="Product Reviews Delete",
        description="""This endpoint allows you to delete a product review.""",
        tags=shop_tag,
    ),
)
class ProductReview(APIView):
    serializer_class = serializers.CreateReviewSerializer
    pagination_class = CustomNumberPagination

    def get_object(self, **kwargs):
        product = Product.objects.get_or_none(slug=kwargs['prod_slug'])
        if not product:
            raise ValidationError("Product doesn't exist")
        return product

    def get(self, request, *args, **kwargs):
        product = self.get_object(**kwargs)
        reviews = product.reviews.select_related('user')
        filter_set = ReviewFilter(data=request.query_params, queryset=reviews)
        if not filter_set.is_valid():
            raise ValidationError('Bad request, check query parameters')
        paginator = self.pagination_class()
        pf_queryset = paginator.paginate_queryset(filter_set.qs, request)
        serializer = serializers.ReviewSerializer(pf_queryset, many=True, exclude_fields=['product'])
        return paginator.get_paginated_response(data={
            'product': product.name,
            'rating': product.get_rating,
            'reviews': serializer.data},
        )

    def post(self, request, *args, **kwargs):
        product = self.get_object(**kwargs)
        data_serializer = self.serializer_class(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        review, created = Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults=data_serializer.validated_data
        )
        status_code = 201 if created else 200
        serializer = serializers.ReviewSerializer(instance=review)
        return Response(data=serializer.data, status=status_code)

    def delete(self, request, *args, **kwargs):
        product = self.get_object(**kwargs)
        review = product.reviews.get_or_none(user=request.user)
        if not review:
            raise ValidationError("You have no review for this product")
        review.hard_delete()
        return Response(data={'message': 'Successfully deleted'}, status=200)


