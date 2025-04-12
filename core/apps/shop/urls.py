from django.urls import path

from .views import CategoriesView, DeleteCategoryView, ProductByCategoryView, ListProductView, ProductView


urlpatterns = [
    path('categories/', CategoriesView.as_view(), name='get_categories'),
    # path('categories/<slug:cat_slug>', DeleteCategoryView.as_view(), name='delete_category'),
    path('categories/<slug:cat_slug>', ProductByCategoryView.as_view()),
    path('products/', ListProductView.as_view(), name='products'),
    path('products/<slug:prod_slug>', ProductView.as_view(), name='product'),

]