from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import CreateUserSerializer, CustomTokenObtainPairSerializer


auth_tag = ['Authentication']


class RegisterApiView(APIView):
    serializer_class = CreateUserSerializer

    @extend_schema(
        summary="Register a new User",
        description="""This endpoint allows to register yourself as a new user.""",
        tags=auth_tag
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'success'}, status=201)
        return Response(serializer.errors, status=400)


@extend_schema_view(
    post=extend_schema(
        summary="Retrieve a Token",
        tags=auth_tag
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Refresh User's token",
        tags=auth_tag
    )
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Verify User's token",
        tags=auth_tag
    )
)
class CustomTokenVerifyView(TokenVerifyView):
    pass
