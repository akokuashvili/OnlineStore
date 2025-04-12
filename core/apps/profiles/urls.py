from django.urls import path

from .views import ProfileView, ShippingAddressView, ShippingAddressViewID


urlpatterns = [
    path('', ProfileView.as_view(), name='get_profile'),
    path('shipping_addresses/', ShippingAddressView.as_view(), name='get_addresses'),
    path('shipping_addresses/detail/<str:id>', ShippingAddressViewID.as_view()),
]