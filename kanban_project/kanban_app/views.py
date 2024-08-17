from django.forms import ValidationError
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response

from .authentication import FirebaseAuthentication
from .models import Board, Column, Task, FirebaseUser
from .serializers import (
    BoardSerializer,
    ColumnSerializer,
    TaskSerializer,
    FirebaseUserSerializer,
)
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Board
from .serializers import BoardSerializer
from rest_framework import generics


class BoardListCreateView(generics.ListCreateAPIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def create(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# View to retrieve, update, and delete a board
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


# View to create and list columns
class ColumnListCreateView(generics.ListCreateAPIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    def get_queryset(self):
        user = self.request.user
        return Column.objects.filter(board__user=user)


# View to retrieve, update, and delete a column
class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


# View to create and list tasks
class TaskListCreateView(generics.ListCreateAPIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(column__board__user=user)

    def perform_create(self, serializer):
        serializer.save()


# View to retrieve, update, and delete a task
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# View to create a Firebase user
class CreateFirebaseUserView(generics.CreateAPIView):
    queryset = FirebaseUser.objects.all()
    serializer_class = FirebaseUserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["email"] = self.request.data.get("email")  # Add email to context
        return context
