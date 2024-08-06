from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer
from rest_framework import status
from rest_framework import generics

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user, created = user.objects.get_or_create(
                username=validated_data['username'],
                defaults={'email': validated_data['email']}
            )
            
            if created:
                user.set_password(validated_data['password'])
                user.save()
            else:
                return Response({'detail': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'image' in validated_data:
                user.image = validated_data['image']
                user.save()
            
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'image': user.image.url if user.image else None
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)