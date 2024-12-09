
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from DABubble.models import ThreadChannelModel, ThreadMessageModel, MessageModel
from DABubble.serializers import ThreadMessageSerializer

class ThreadMessageView(APIView):
    """
    ThreadMessageView handles the creation, retrieval, and updating of messages within a specific thread channel.

    HTTP Methods:
    - POST: Creates a new message in a thread channel.
    - GET: Retrieves all messages within a specific thread channel.
    - PATCH: Updates an existing message within a thread channel.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - The request for POST and PATCH methods should include the message content.
    - POST and PATCH methods associate the message with the specified `thread_channel_id`.
    - GET method retrieves all messages associated with the specified `thread_channel_id`.

    Attributes:
    - authentication_classes: A list containing token-based authentication for the view.
    - permission_classes: A list of permissions that restrict access to authenticated users only.
    """
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
    """
    ThreadEmojiView handles the updating of emoji reactions for messages in a thread channel.

    HTTP Methods:
    - PATCH: Updates the emoji reactions (hands up, check, nerd, and rocket) for a specific message within a thread channel.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - The request should include lists of users for each emoji type.
    - The emoji reactions are updated for the specified message in the thread channel.
    - The Many-to-Many relationship fields for each emoji type (handsup, check, nerd, rocket) are updated with the provided user data.

    Attributes:
    - authentication_classes: A list containing token-based authentication for the view.
    - permission_classes: A list of permissions that restrict access to authenticated users only.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        thread_channel_id = kwargs.get('thread_channel_id')
        thread_message_id = kwargs.get('message_id')
    
        try:
            threadMessage = ThreadMessageModel.objects.get(id=thread_message_id, thread_channel_id=thread_channel_id)
        except MessageModel.DoesNotExist:
            return Response({'detail': 'Message or Channel not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # List of dicts containing user data for each emoji type
        emoji_handsup_users = request.data.get('emoji_handsup', [])
        emoji_check_users = request.data.get('emoji_check', [])
        emoji_nerd_users = request.data.get('emoji_nerd', [])
        emoji_rocket_users = request.data.get('emoji_rocket', [])
        # Convert the user data dictionaries into User model instances
        handsup_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_handsup_users]
        check_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_check_users]
        nerd_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_nerd_users]
        rocket_users = [User.objects.get(id=user_dict['id']) for user_dict in emoji_rocket_users]
        # Update the ManyToMany fields with the user instances
        threadMessage.emoji_handsup.set(handsup_users)
        threadMessage.emoji_check.set(check_users)
        threadMessage.emoji_nerd.set(nerd_users)
        threadMessage.emoji_rocket.set(rocket_users)
        
        threadMessage.save()

        serializer = ThreadMessageSerializer(threadMessage)
        return Response(serializer.data, status=status.HTTP_200_OK)