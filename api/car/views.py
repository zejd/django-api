from rest_framework import views, status, response, exceptions, permissions, filters, generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from user import services
from . import models
from . import serializer as car_serializer


class CarsAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        cars = models.Car.objects.all()
        serializer = car_serializer.CarSerializer(cars, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = car_serializer.CarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)

class CarDetailsApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        car_id = kwargs.get('id')
        authenticator = JWTAuthentication()
        user_from_token, token = authenticator.authenticate(request)
        user_id_from_token = token.payload['user_id']
        car = models.Car.objects.get(id=car_id)
        if not car:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if car.user.id != user_id_from_token and not services.is_admin_user(user_id_from_token):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        serializer = car_serializer.CarSerializer(car)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        car_id = kwargs.get('id')
        authenticator = JWTAuthentication()
        user_from_token, token = authenticator.authenticate(request)
        user_id_from_token = token.payload['user_id']
        car_obj = models.Car.objects.get(id=car_id)
        if not car_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if car_obj.user.id != user_id_from_token and not services.is_admin_user(user_id_from_token):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        serializer = car_serializer.CarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        car = serializer.validated_data
        car_obj.make = car['make']
        car_obj.model = car['model']
        car_obj.year = car['year']
        car_obj.user = car['user']
        car_obj.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        authenticator = JWTAuthentication()
        user_from_token, token = authenticator.authenticate(request)
        user_id_from_token = token.payload['user_id']
        car_id = kwargs.get('id')
        car = models.Car.objects.get(id=car_id)
        if not car:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        if car.user.id != user_id_from_token and not services.is_admin_user(user_id_from_token):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        car.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class CarsByUserAPI(views.APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        authenticator = JWTAuthentication()
        user_from_token, token = authenticator.authenticate(request)
        user_id_from_token = token.payload['user_id']

        if user_id != user_id_from_token and not services.is_admin_user(user_id_from_token):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        cars = models.Car.objects.filter(user=user_id)
        serializer = car_serializer.CarSerializer(cars, many=True)
        return response.Response(serializer.data)