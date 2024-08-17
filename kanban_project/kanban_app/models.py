from django.db import models
from django.contrib.auth.models import User


class FirebaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.uid}"


class Board(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")

    def __str__(self):
        return self.name


class Column(models.Model):
    name = models.CharField(max_length=255)
    board = models.ForeignKey(Board, related_name="columns", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    column = models.ForeignKey(Column, related_name="tasks", on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Todo")

    def __str__(self):
        return self.title

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Board, Column, Task


@receiver(post_save, sender=User)
def assign_default_permissions(sender, instance, created, **kwargs):
    if created:
        # Get or create the 'BasicUser' group
        basic_group, created = Group.objects.get_or_create(name="BasicUser")

        # Define permissions for each model
        board_content_type = ContentType.objects.get_for_model(Board)
        column_content_type = ContentType.objects.get_for_model(Column)
        task_content_type = ContentType.objects.get_for_model(Task)

        permissions = Permission.objects.filter(
            content_type__in=[
                board_content_type,
                column_content_type,
                task_content_type,
            ]
        )

        # Assign all permissions to the BasicUser group
        basic_group.permissions.set(permissions)

        # Add the user to the 'BasicUser' group
        instance.groups.add(basic_group)
