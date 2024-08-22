import logging
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, UserSerializer, MessageSerializer, ChannelSerializer, privateChannelSerializer
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CustomAuthTokenSerializer
from .models import AvatarModel, ChannelModel, MessageModel, PrivateChannelModel
from .serializers import AvatarModelSerializer, ChannelSerializer
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import models


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
            'id': user.pk,
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
            'id': user.pk,
            'email': user.email
        })
        
class AvatarModelViewSet(viewsets.ModelViewSet):
    queryset = AvatarModel.objects.all()
    serializer_class = AvatarModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Hier wird der authentifizierte Benutzer dem Avatar zugewiesen
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
            

class AvatarUserModelView(APIView):
    serializer_class= AvatarModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            avatar = AvatarModel.objects.get(user=user)  # AvatarModel für den authentifizierten Benutzer abrufen
        except AvatarModel.DoesNotExist:
            return Response({"error": "Avatar not found for the user."}, status=status.HTTP_404_NOT_FOUND)

        # AvatarModel-Objekt serialisieren
        serializer = AvatarModelSerializer(avatar)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Löschen des Tokens
        request.auth.delete()
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
    

class UsersView(APIView):
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ChannelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        channels = ChannelModel.objects.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SingleChannelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
            serializer = ChannelSerializer(channel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChannelModel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
    def put(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
            serializer = ChannelSerializer(channel, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChannelModel.DoesNotExist:
            return Response({'error': 'Channel name cant updated'}, status=status.HTTP_404_NOT_FOUND)
    
class MessageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
        except ChannelModel.DoesNotExist:
            return Response({'detail': 'Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, channel=channel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
            messages = MessageModel.objects.filter(channel = channel) # Filtere Nachrichte nach nur aus diesem Channel
            serializer = MessageSerializer(messages, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChannelModel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
    
class PrivateChannelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        member_ids = request.data.get('channelMembers')
        if len(member_ids) >= 3:
            return Response({'error': 'A private channel must have exactly two members.'}, status=status.HTTP_400_BAD_REQUEST)

        existing_channels = PrivateChannelModel.objects.annotate(
            num_members=models.Count('channelMembers')
        ).filter(
            num_members=2
        ).filter(
            channelMembers=member_ids[0]
        ).filter(
            channelMembers=member_ids[1]
        ).distinct()

        if existing_channels.exists():
            return Response({'error': 'A private channel between these users already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = privateChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = request.user
        channels = PrivateChannelModel.objects.filter(channelMembers=user)
        serializer = privateChannelSerializer(channels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        