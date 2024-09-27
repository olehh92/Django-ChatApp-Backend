import logging
from django.conf import settings
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, UserSerializer, MessageSerializer, ChannelSerializer, ThreadChannelSerializer, ThreadMessageSerializer
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CustomAuthTokenSerializer
from .models import AvatarModel, ChannelModel, MessageModel, ThreadChannelModel, ThreadMessageModel
from .serializers import AvatarModelSerializer, ChannelSerializer
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


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

    def post(self, request, *args, **kwargs):
        data = request.data.copy() 

        serializer = ChannelSerializer(data=data) 
        if serializer.is_valid():
            serializer.save(createdFrom=request.user)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChannelModel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)


class MessageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
        except ChannelModel.DoesNotExist:
            return Response({'detail': 'Channel not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, channel=channel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        try:
            channel = ChannelModel.objects.get(id=channel_id)
            messages = MessageModel.objects.filter(channel=channel)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChannelModel.DoesNotExist:
            return Response({'detail': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        message_id = kwargs.get('message_id')

        try:
            message = MessageModel.objects.get(id=message_id, channel__id=channel_id)
        except MessageModel.DoesNotExist:
            return Response({'detail': 'Message or Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        content = request.data.get('content')
        if content:
            message.content = content

        thread_open = request.data.get('threadOpen', message.threadOpen)
        if thread_open and not message.thread_channel:
            thread_channel = ThreadChannelModel.objects.create(
                threadName=f'Thread for message {message.id}',
                threadDescription=f'Thread started from message {message.id} in channel {channel_id}',
                mainChannel=message.channel,
                createdFrom=request.user,
                original_message=message
            )
            thread_channel.threadMember.add(request.user)

            message.thread_channel = thread_channel
            message.threadOpen = True
            message.save()

            ThreadMessageModel.objects.create(
                sender=message.sender,
                content=message.content,
                thread_channel=thread_channel
            )

        message.threadOpen = thread_open
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
class MessageEmojiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        message_id = kwargs.get('message_id')
        
        try:
            message = MessageModel.objects.get(id=message_id, channel__id=channel_id)
        except MessageModel.DoesNotExist:
            return Response({'detail': 'Message or Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Listen von Diktaten, die die Benutzerdaten enthalten
        emoji_handsup_users = request.data.get('emoji_handsup', [])
        emoji_check_users = request.data.get('emoji_check', [])
        emoji_nerd_users = request.data.get('emoji_nerd', [])
        emoji_rocket_users = request.data.get('emoji_rocket', [])
        # Konvertiere die Diktate in User-Objekte
        handsup_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_handsup_users]
        check_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_check_users]
        nerd_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_nerd_users]
        rocket_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_rocket_users]
        # Aktualisiere die ManyToMany-Felder mit den User-Objekten
        message.emoji_handsup.set(handsup_users)
        message.emoji_check.set(check_users)
        message.emoji_nerd.set(nerd_users)
        message.emoji_rocket.set(rocket_users)
        
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ThreadMessageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        thread_channel_id = kwargs.get('thread_channel_id')
        try:
            thread_channel = ThreadChannelModel.objects.get(id=thread_channel_id)
        except ThreadChannelModel.DoesNotExist:
            return Response({'detail': 'Thread Channel not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ThreadMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, thread_channel=thread_channel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        thread_channel_id = kwargs.get('thread_channel_id')
        try:
            thread_channel = ThreadChannelModel.objects.get(id=thread_channel_id)
            messages = ThreadMessageModel.objects.filter(thread_channel=thread_channel)
            serializer = ThreadMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ThreadChannelModel.DoesNotExist:
            return Response({'detail': 'Thread Channel not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, *args, **kwargs):
        thread_channel_id = kwargs.get('thread_channel_id')
        thread_message_id = kwargs.get('message_id')
        
        try:
            threadMessage = ThreadMessageModel.objects.get(id=thread_message_id, thread_channel=thread_channel_id)
        except MessageModel.DoesNotExist:
            return Response({'detail': 'Message or Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        content = request.data.get('content')
        if content:
            threadMessage.content = content
            
        
        
        threadMessage.save()

        serializer = ThreadMessageSerializer(threadMessage)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ThreadEmojiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        thread_channel_id = kwargs.get('thread_channel_id')
        thread_message_id = kwargs.get('message_id')
    
        try:
            threadMessage = ThreadMessageModel.objects.get(id=thread_message_id, thread_channel_id=thread_channel_id)
        except MessageModel.DoesNotExist:
            return Response({'detail': 'Message or Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Listen von Diktaten, die die Benutzerdaten enthalten
        emoji_handsup_users = request.data.get('emoji_handsup', [])
        emoji_check_users = request.data.get('emoji_check', [])
        emoji_nerd_users = request.data.get('emoji_nerd', [])
        emoji_rocket_users = request.data.get('emoji_rocket', [])
        # Konvertiere die Diktate in User-Objekte
        handsup_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_handsup_users]
        check_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_check_users]
        nerd_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_nerd_users]
        rocket_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_rocket_users]
        # Aktualisiere die ManyToMany-Felder mit den User-Objekten
        threadMessage.emoji_handsup.set(handsup_users)
        threadMessage.emoji_check.set(check_users)
        threadMessage.emoji_nerd.set(nerd_users)
        threadMessage.emoji_rocket.set(rocket_users)
        
        threadMessage.save()

        serializer = ThreadMessageSerializer(threadMessage)
        return Response(serializer.data, status=status.HTTP_200_OK)




class PasswordRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('emailName')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email does not exist"}, status=400)

        token = default_token_generator.make_token(user)
        reset_link = f'http://localhost:4200/reset-password?token={token}&uid={user.pk}'

        subject = 'DABubble Password Reset Request'
        html_content = render_to_string('password_reset_email.html', {
            'username': user.username,
            'reset_link': reset_link,
        })

        text_content = strip_tags(html_content)

        send_mail(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=html_content
        )

        return JsonResponse({"message": "Password reset link sent successfully"}, status=200)
