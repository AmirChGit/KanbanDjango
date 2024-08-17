import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin.credentials import Certificate
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# Import your models here
from .models import Board, Column, Task  # Import Board, Column, Task models

# Initialize the Firebase Admin SDK if it hasn't been initialized already
if not firebase_admin._apps:
    cred = Certificate(
        settings.FIREBASE_CERT_PATH
    )  # Use your Firebase service account key file path
    firebase_admin.initialize_app(cred)


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]
            try:
                user = User.objects.get(username=uid)
            except User.DoesNotExist:
                user = User.objects.create(username=uid)
                # Assign user to the BasicUser group or assign specific permissions
                basic_group, created = Group.objects.get_or_create(name="BasicUser")
                if created:
                    # Assign permissions for Board, Column, Task models to this group
                    content_types = ContentType.objects.get_for_models(
                        Board, Column, Task
                    )
                    permissions = Permission.objects.filter(
                        content_type__in=content_types.values()
                    )
                    basic_group.permissions.set(permissions)
                user.groups.add(basic_group)

            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(f"Invalid Firebase token: {str(e)}")
