from rest_framework.response import Response
from rest_framework import status
from DABubble.serializers import AvatarModelSerializer
from DABubble.models import AvatarModel
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class AvatarModelViewSet(viewsets.ModelViewSet):
    """
    AvatarModelViewSet handles CRUD operations for the AvatarModel.

    HTTP Methods:
    - GET: Retrieve a list of avatars or a specific avatar instance.
    - POST: Create a new avatar associated with the authenticated user.
    - PUT/PATCH: Update an existing avatar instance.
    - DELETE: Delete an avatar instance.

    Attributes:
    - queryset: Retrieves all instances of the AvatarModel.
    - serializer_class: Specifies the serializer to use (AvatarModelSerializer).
    - authentication_classes (list): Specifies the authentication backend used (TokenAuthentication).
    - permission_classes (list): Ensures that only authenticated users can access this endpoint.
    """
    queryset = AvatarModel.objects.all()
    serializer_class = AvatarModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
            

class AvatarUserModelView(APIView):
    """
    AvatarUserModelView provides functionality to retrieve the avatar of the authenticated user.

    HTTP Methods:
    - GET: Retrieves the avatar associated with the current authenticated user.

    Attributes:
    - serializer_class: Specifies the serializer to use (AvatarModelSerializer).
    - authentication_classes (list): Specifies the authentication backend used (TokenAuthentication).
    - permission_classes (list): Ensures that only authenticated users can access this endpoint.
    """
    serializer_class= AvatarModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            avatar = AvatarModel.objects.get(user=user) 
        except AvatarModel.DoesNotExist:
            return Response({"error": "Avatar not found for the user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AvatarModelSerializer(avatar)
        return Response(serializer.data, status=status.HTTP_200_OK)