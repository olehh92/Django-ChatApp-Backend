from rest_framework.response import Response
from DABubble.serializers import MessageSerializer
from rest_framework import status
from django.contrib.auth.models import User
from DABubble.models import ChannelModel, MessageModel, ThreadChannelModel, ThreadMessageModel
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class MessageView(APIView):
    """
    MessageView handles operations related to messages within a specific channel.

    HTTP Methods:
    - POST: Creates a new message in the specified channel.
    - GET: Retrieves all messages for a specific channel.
    - PATCH: Updates an existing message, including the creation of a thread for the message.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - On POST:
        - Creates a new message within the specified channel.
        - Associates the message with the user sending it and the channel provided.
        - Returns the created message data on success.
        - Returns an error if the channel is not found.
    - On GET:
        - Retrieves all messages from a specific channel.
        - Returns a list of messages for the channel.
        - Returns an error if the channel does not exist.
    - On PATCH:
        - Updates an existing message in a specific channel.
        - Allows the creation of a thread for the message.
        - Returns the updated message data on success.
        - Returns an error if the message or channel is not found.
    """
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
    """
    MessageEmojiView handles the updating of emoji reactions on a specific message in a channel.

    HTTP Method:
    - PATCH: Updates emoji reactions (e.g., hands-up, check, nerd, rocket) for a specific message in a channel.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - The request should contain the updated lists of users for each emoji reaction (hands-up, check, nerd, and rocket).
    - Each emoji type is associated with a list of user IDs indicating which users reacted with that emoji.
    - The method updates the corresponding `ManyToMany` relationships in the `MessageModel`.
    - Returns the updated message data upon successful update.

    Attributes:
    - authentication_classes: A list containing token-based authentication for the view.
    - permission_classes: A list of permissions that restrict access to authenticated users only.
    """
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