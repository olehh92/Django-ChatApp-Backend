from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AvatarModel, ChannelModel, MessageModel, ThreadMessageModel, ThreadChannelModel
from rest_framework.serializers import ModelSerializer

class RegistrationSerializer(serializers.ModelSerializer):

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
    class Meta:
        model = AvatarModel
        fields = ['id', 'user', 'image', 'image_path']
        read_only_fields = ['user']  # Verhindert, dass das 'user'-Feld vom Client gesetzt wird

    def validate(self, data):
        # Setze den Standardwert für image_path, wenn image nicht gesetzt ist
        if not data.get('image') and not data.get('image_path'):
            data['image_path'] = AvatarModel.default_image_path
        return data

    def create(self, validated_data):
        # Das user-Feld sollte hier nicht gesetzt werden, weil es in der View zugewiesen wird
        return AvatarModel.objects.create(**validated_data)
    
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'id']
        
        
class ThreadMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadMessageModel
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender']

class MessageSerializer(serializers.ModelSerializer):
    thread_channel = serializers.PrimaryKeyRelatedField(read_only=True)  # Read-only for now

    class Meta:
        model = MessageModel
        fields = ['id', 'channel', 'sender', 'content', 'timestamp', 'threadOpen', 'thread_channel']
        read_only_fields = ['sender']

class ChannelSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)  # Channel has many messages
    channelMembers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = ChannelModel
        fields = ['id', 'channelName', 'channelDescription', 'channelMembers', 'messages', 'createdFrom', 'privateChannel']

class ThreadChannelSerializer(serializers.ModelSerializer):
    thread_messages = ThreadMessageSerializer(many=True, read_only=True)  # Thread has many messages

    class Meta:
        model = ThreadChannelModel
        fields = ['id', 'threadName', 'threadDescription', 'mainChannel', 'createdFrom', 'threadMember', 'original_message', 'thread_messages']