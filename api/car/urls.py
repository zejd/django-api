from django.urls import path
from .views import CarsAPIView, CarDetailsApi, CarsByUserAPI

urlpatterns = [
    path('cars/', CarsAPIView.as_view(), name='cars'),
    path('cars/<int:id>', CarDetailsApi.as_view(), name='car_detail'),
    path('cars/user/<int:id>', CarsByUserAPI.as_view(), name='cars_by_user')
]