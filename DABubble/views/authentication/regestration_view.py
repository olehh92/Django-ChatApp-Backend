import logging
from django.conf import settings
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from DABubble.serializers import RegistrationSerializer
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class RegistrationView(generics.CreateAPIView):
    """
    RegistrationView handles user registration.

    HTTP Methods:
    - POST: Creates a new user account if the provided data is valid and the username does not already exist.

    Behavior:
    - Accepts registration details such as username, email, first name, last name, and password.
    - Validates the input data using the `RegistrationSerializer`.
    - Checks if a user with the provided username already exists.
    - Creates a new user and generates an authentication token if the user does not exist.
    - Returns the authentication token and user details upon successful registration.
    - Returns an error message if validation fails or the user already exists.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        # Logging der initialen Daten
        logger.debug(f'Initial data: {serializer.initial_data}')
        
        if not serializer.is_valid():
            # Logging der Fehler
            logger.error(f'Validation errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        logger.debug(f'Validated data: {validated_data}')
        
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={
                'email': validated_data['email'],
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name']
            }
        )
        
        if created:
            user.set_password(validated_data['password'])
            user.save()
        else:
            return Response({'detail': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'email': user.email
        })