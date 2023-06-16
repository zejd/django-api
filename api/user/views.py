from rest_framework import views, status, response, exceptions, permissions, filters
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.generics import ListAPIView
from django.db.models import Q
from . import serializer as user_serializer
from . import services
from . import models


class RegisterApi(views.APIView):

    def post(self, request):
        serializer = user_serializer.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = services.user_email_selector(email=data.email)
        if user is not None:
            return Response(data="User With That Email Already Exists", status=status.HTTP_400_BAD_REQUEST)
        serializer.instance = services.create_user(user=data)

        return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)

class CreateAdminUserApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    def post(self, request):
        serializer = user_serializer.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = services.user_email_selector(email=data.email)
        if user is not None:
            return Response(data="User With That Email Already Exists", status=status.HTTP_400_BAD_REQUEST)
        serializer.instance = services.create_super_user(user=data)

        return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)

# Custom login
class LoginApi(views.APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = services.user_email_selector(email=email)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")

        token = services.create_token(user_id=user.id)

        return response.Response({"jwt": token})


class UserApi(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        authenticator = JWTAuthentication()
        try:
            email, token = authenticator.authenticate(request)
            user_id_from_token = token.payload['user_id']
            user_id = kwargs.get('id')
            if user_id_from_token != user_id and not services.is_admin_user(user_id_from_token):
                return response.Response(status=status.HTTP_403_FORBIDDEN)
            user = services.get_user_by_id(user_id)
            return response.Response(user)

        except AuthenticationFailed:
            return response.Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        authenticator = JWTAuthentication()
        try:
            user_from_token, token = authenticator.authenticate(request)
            user_id_from_token = token.payload['user_id']
            user_id = kwargs.get('id')
            if user_id_from_token != user_id:
                return response.Response(status=status.HTTP_403_FORBIDDEN)

            user = models.User.objects.get(id=user_id)
            serializer = user_serializer.UserSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            user = services.user_email_selector(email=data.email)

            if user is not None and data.email != user_from_token.email:
                return Response(data="User With That Email Already Exists", status=status.HTTP_400_BAD_REQUEST)

            serializer.instance = services.update_user(user=data, user_id=user_id)
            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        except AuthenticationFailed:
            return response.Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        authenticator = JWTAuthentication()
        try:
            user_from_token, token = authenticator.authenticate(request)
            user_id_from_token = token.payload['user_id']
            user_id = kwargs.get('id')
            if not services.is_admin_user(user_id_from_token):
                return response.Response(status=status.HTTP_403_FORBIDDEN)
            user = models.User.objects.get(id=user_id)
            if not user:
                return response.Response(status=status.HTTP_404_NOT_FOUND)
            user.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except AuthenticationFailed:
            return response.Response(status=status.HTTP_403_FORBIDDEN)


class UsersApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        users = services.get_all_users()
        return response.Response(users)


class FilterUsersApi(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = user_serializer.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def get_queryset(self):
        queryset = models.User.objects.all()
        search_params = self.request.query_params.get('search')

        if search_params:
            queryset = queryset.filter(
                Q(first_name__icontains=search_params) |
                Q(last_name__icontains=search_params) |
                Q(email__icontains=search_params)
            )

        return queryset
