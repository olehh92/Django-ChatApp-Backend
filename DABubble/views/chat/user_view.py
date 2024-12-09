import logging
from rest_framework.response import Response
from DABubble.serializers import UserSerializer
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


logger = logging.getLogger(__name__)

class UsersView(APIView):
    """
    UsersView handles retrieving and updating user information.

    HTTP Methods:
    - GET: Retrieves a list of all users' basic information (id, first name, last name, email, username).
    - PUT: Updates the authenticated user's information (partial updates allowed).

    Attributes:
    - authentication_classes: Specifies that this view requires token-based authentication.
    - permission_classes: Restricts access to authenticated users only.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        users = User.objects.all().values('id', 'first_name', 'last_name', 'email', 'username')
        return Response(list(users), status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ActiveUserView(APIView):
    """
    ActiveUserView handles retrieving information about the currently authenticated user.

    HTTP Methods:
    - GET: Retrieves the authenticated user's data.

    Attributes:
    - authentication_classes: Specifies that this view requires token-based authentication.
    - permission_classes: Restricts access to authenticated users only.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    