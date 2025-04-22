import django_filters

from .models import Product, Review


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    max_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='gte')
    in_stock = django_filters.NumberFilter(lookup_expr='gte')
    created_at = django_filters.DateTimeFilter(lookup_expr='gte')
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price_current', 'price'),
            ('name', 'name')
        )
    )

    class Meta:
        model = Product
        fields = ['name', 'max_price', 'min_price', 'in_stock', 'created_at']


class ReviewFilter(django_filters.FilterSet):
    created_at = django_filters.DateTimeFilter(lookup_expr='gte')
    rating = django_filters.NumberFilter(lookup_expr='exact')
    ordering = django_filters.OrderingFilter(fields=(('rating', 'rating'),))

    class Meta:
        model = Review
        fields = ['created_at', 'rating']