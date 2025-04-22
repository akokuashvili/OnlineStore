from django.urls import path

from . import views


urlpatterns = [
    path('', views.ProfileView.as_view(), name='get_profile'),
    path('shipping_addresses/', views.ShippingAddressView.as_view(), name='get_addresses'),
    path('shipping_addresses/<str:id>', views.ShippingAddressDetailView.as_view()),
    path('orders/', views.OrdersView.as_view()),
    path('orders/<str:tx_ref>', views.OrderItemsView.as_view()),
    path('reviews/', views.ReviewsListView.as_view())
]