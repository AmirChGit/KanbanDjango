from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Board, Column, Task, FirebaseUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class FirebaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseUser
        fields = ["uid"]

    def create(self, validated_data):
        uid = validated_data.get("uid")
        email = self.context["email"]

        # Create a Django user with the UID as the username
        user = User.objects.create_user(username=uid, email=email)

        # Create the FirebaseUser and associate it with the Django user
        firebase_user = FirebaseUser.objects.create(user=user, uid=uid)
        return firebase_user


class BoardSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Board
        fields = ["id", "name", "user"]

    def to_representation(self, instance):
        # Customize how the 'user' field is represented
        representation = super().to_representation(instance)
        representation["user"] = instance.user.username  # Use the username as the UID
        return representation

    def to_internal_value(self, data):
        # Convert the UID (which is stored in 'username') back to the User instance
        internal_value = super().to_internal_value(data)
        try:
            user = User.objects.get(username=data.get("user"))
            internal_value["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with UID not found.")
        return internal_value


class ColumnSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Column
        fields = ["id", "name", "board", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.username  # Convert User instance to UID
        return representation

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        try:
            user = User.objects.get(username=data.get("user"))
            internal_value["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with UID not found.")
        return internal_value


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "column", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.username  # Convert User instance to UID
        return representation

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        try:
            user = User.objects.get(username=data.get("user"))
            internal_value["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with UID not found.")
        return internal_value
