from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path("register/", views.RegisterApi.as_view(), name="register"),
    path("register/admin/", views.CreateAdminUserApi.as_view(), name="create_admin"),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path("users/", views.FilterUsersApi.as_view(), name="users"),
    path("users/<int:id>", views.UserApi.as_view(), name="user"),
]