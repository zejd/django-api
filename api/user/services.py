import dataclasses
from datetime import date, datetime, timedelta
import jwt
from typing import TYPE_CHECKING
from django.conf import settings
from . import models
from . import serializer as user_serializer, authentication
from .models import User


@dataclasses.dataclass
class UserDataClass:
    first_name: str
    last_name: str
    email: str
    password: str = None
    phone_number: str = None
    id: int = None

    @classmethod
    def from_instance(cls, user: "User") -> "UserDataClass":
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            id=user.id
        )



def create_user(user: "UserDataClass") -> "UserDataClass":
    instance = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number
    )
    if user.password is not None:
        instance.set_password(user.password)

    instance.save()

    return UserDataClass.from_instance(instance)

def create_super_user(user: "UserDataClass") -> "UserDataClass":
    instance = models.User.objects.create_superuser(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        password=user.password
    )

    return UserDataClass.from_instance(instance)

def update_user(user: User, user_id: int) -> "UserDataClass":
    models.User.objects.filter(id=user_id).update(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number
    )

    return UserDataClass.from_instance(user)

def user_email_selector(email: str) -> User:
    user = models.User.objects.filter(email=email).first()

    return user

def get_all_users() -> list[User]:
    users = models.User.objects.all()
    serializer = user_serializer.UserSerializer(users, many=True)
    return serializer.data


def get_user_by_id(user_id: str) -> User:
    user = models.User.objects.get(pk=user_id)

    serializer = user_serializer.UserSerializer(user)
    return serializer.data

def is_admin_user(user_id: str) -> bool:
    user = models.User.objects.get(pk=user_id)
    return user.is_superuser


def get_user_id_from_jwt(jwt_token) -> int:
    try:
        decoded_token = jwt.decode(jwt_token, verify=True, algorithms=["HS256"])
        print(decoded_token)
        user_id = decoded_token['user_id']
        return user_id
    except jwt.DecodeError:
        raise ValueError('Invalid JWT token')

def extract_jwt_from_headers(request) -> str:
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        jwt_token = auth_header.split('Bearer ')[1]
        return jwt_token
    raise ValueError('Invalid JWT token')

#Custom token
def create_token(user_id: int) -> str:
    payload = dict(
        id=user_id,
        exp=json_date_serial(datetime.utcnow() + timedelta(hours=24)),
        iot=json_date_serial(datetime.utcnow())
    )
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def json_date_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))