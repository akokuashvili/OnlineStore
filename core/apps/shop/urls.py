from django.urls import path

from . import views


urlpatterns = [
    path('categories/', views.CategoriesView.as_view(), name='get_categories'),
    path('categories/<slug:cat_slug>', views.DeleteCategoryView.as_view(), name='delete_category'),
    path('categories/<slug:cat_slug>', views.ProductByCategoryView.as_view()),
    path('products/', views.ListProductView.as_view(), name='products'),
    path('products/seller/<slug:seller_slug>', views.ProductBySellerView.as_view(), name='products_by_seller'),
    path('products/<slug:prod_slug>', views.ProductView.as_view(), name='product'),
    path('cart/', views.CartView.as_view()),
    path('checkout/', views.CheckoutView.as_view()),

]