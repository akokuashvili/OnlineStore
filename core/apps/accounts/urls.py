from django.urls import path

from . import views


urlpatterns = [
    path('', views.RegisterApiView.as_view(), name='registration'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', views.CustomTokenVerifyView.as_view(), name='token_verify'),
]