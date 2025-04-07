from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import ProfileSerializer


profile_tag = ['Profiles']


class ProfileView(APIView):
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="Retrieve Profile",
        description="""
                This endpoint allows a user to retrieve profile.
            """,
        tags=profile_tag,
    )
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Update Profile",
        description="""
                    This endpoint allows a user to update profile.
                """,
        tags=profile_tag,
        # request={"multipart/form-data": serializer_class},
    )
    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    # def patch(self, request):
    #     serializer = self.serializer_class(request.user, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)

    @extend_schema(
        summary="Deactivate account",
        description="""
                This endpoint allows a user to deactivate account.
            """,
        tags=profile_tag,
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': f'Account {user.email} deactivated'})
