from rest_framework.response import Response
from DABubble.serializers import ChannelSerializer
from rest_framework import status
from DABubble.models import ChannelModel, MessageModel, ThreadChannelModel, ThreadMessageModel
from DABubble.serializers import ChannelSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class ChannelView(APIView):
    """
    ChannelView handles operations related to channels.

    HTTP Methods:
    - POST: Allows authenticated users to create a new channel.
    - GET: Retrieves a list of all existing channels.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - On POST:
        - Validates the incoming data using `ChannelSerializer`.
        - Saves the new channel with the authenticated user as the creator.
        - Returns the created channel's data on success.
        - Returns validation errors if the data is invalid.
    - On GET:
        - Fetches all channels from the database.
        - Serializes the data and returns the list of channels.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        
        channel_name = data.get("channelName")
        if ChannelModel.objects.filter(channelName__iexact=channel_name).exists():
            return Response(
                {"error": "A channel with this name already exists."},
                status=status.HTTP_400_BAD_REQUEST
            ) 

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
    """
    SingleChannelView handles operations on a single channel.

    HTTP Methods:
    - GET: Retrieves a specific channel by its ID.
    - PUT: Updates an existing channel by its ID.

    Behavior:
    - Requires the user to be authenticated via token authentication.
    - On GET:
        - Retrieves the channel with the given `channel_id`.
        - Returns the serialized channel data on success.
        - Returns an error if the channel is not found.
    - On PUT:
        - Retrieves the channel with the given `channel_id` to update.
        - Allows partial updates using the `ChannelSerializer`.
        - Returns the updated channel data on success.
        - Returns validation errors if the update data is invalid.
        - Returns an error if the channel is not found.
    """
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