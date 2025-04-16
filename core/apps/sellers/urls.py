from django.urls import path

from .views import SellerView, SellerProductsView, SellerProductView, \
    SellerOrdersView, SellerOrderItemsView


urlpatterns = [
    path('', SellerView.as_view(), name='seller'),
    path('products/', SellerProductsView.as_view(), name='sellers_products'),
    path('products/<slug:slug>', SellerProductView.as_view(), name='sellers_products'),
    path('orders/', SellerOrdersView.as_view()),
    path('orders/<str:tx_ref>', SellerOrderItemsView.as_view())
]