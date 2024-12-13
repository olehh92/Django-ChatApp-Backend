from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AvatarModel, ChannelModel, MessageModel, ThreadMessageModel, ThreadChannelModel
from rest_framework.serializers import ModelSerializer

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer is used for creating and validating new users.
    The password field is treated as `write_only`, meaning it is only used during user creation.
    """
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if 'password' not in data:
            raise serializers.ValidationError("Password field is required")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user with email and password.

    This serializer checks if the email and password are correct and returns the authenticated user.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password.')

        data['user'] = user
        return data
    
class AvatarModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Avatar model.

    This serializer is used for creating or updating a user's avatar. 
    If neither an image nor an image path is provided, the default image path is used.
    """
    
    class Meta:
        model = AvatarModel
        fields = ['id', 'user', 'image', 'image_path']
        read_only_fields = ['user']

    def validate(self, data):
        if not data.get('image') and not data.get('image_path'):
            data['image_path'] = AvatarModel.default_image_path
        return data

    def create(self, validated_data):
        return AvatarModel.objects.create(**validated_data)
    
class UserSerializer(ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to serialize basic user information such as first name, last name, email, and ID.
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'id']
        
        
class ThreadMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the ThreadMessage model.

    This serializer is used to serialize messages within a thread. 
    It supports emoji reactions and file uploads.
    """
    
    content = serializers.CharField(required=False)
    emoji_handsup = UserSerializer(many=True, required=False)
    emoji_check = UserSerializer(many=True, required=False)
    emoji_nerd = UserSerializer(many=True, required=False)
    emoji_rocket = UserSerializer(many=True, required=False)
    messageData = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = ThreadMessageModel
        fields = ['id', 'sender', 'thread_channel', 'content', 'timestamp', 'emoji_handsup', 'emoji_check', 'emoji_nerd', 'emoji_rocket', 'messageData']
        read_only_fields = ['sender']

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    This serializer is used to serialize messages within a channel. 
    It also supports emoji reactions and file uploads.
    """
    
    content = serializers.CharField(required=False)
    thread_channel = serializers.PrimaryKeyRelatedField(read_only=True)
    emoji_handsup = UserSerializer(many=True, required=False)
    emoji_check = UserSerializer(many=True, required=False)
    emoji_nerd = UserSerializer(many=True, required=False)
    emoji_rocket = UserSerializer(many=True, required=False)
    messageData = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = MessageModel
        fields = ['id', 'channel', 'sender', 'content', 'timestamp', 'threadOpen', 'thread_channel', 'emoji_handsup', 'emoji_check', 'emoji_nerd', 'emoji_rocket', 'messageData']
        read_only_fields = ['sender']

class ChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Channel model.

    This serializer is used to serialize channels, including the messages associated with a channel, 
    as well as the members and creator of the channel.
    """
    
    messages = MessageSerializer(many=True, read_only=True) 
    channelMembers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    createdFrom = UserSerializer(read_only=True)

    class Meta:
        model = ChannelModel
        fields = ['id', 'channelName', 'channelDescription', 'channelMembers', 'messages', 'createdFrom', 'privateChannel']

class ThreadChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for the ThreadChannel model.

    This serializer is used to serialize threads within a channel. 
    It also includes the messages within the thread.
    """
    
    thread_messages = ThreadMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ThreadChannelModel
        fields = ['id', 'threadName', 'threadDescription', 'mainChannel', 'createdFrom', 'threadMember', 'original_message', 'thread_messages']