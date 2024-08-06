import logging
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CustomAuthTokenSerializer


logger = logging.getLogger(__name__)

class LoginView(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        logger.debug(f'Received data: {request.data}')
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })       

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

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
            'user_id': user.pk,
            'email': user.email
        })