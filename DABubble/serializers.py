from rest_framework import serializers
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'password_confirm')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if 'password' not in data:
            raise serializers.ValidationError("Password field is required")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = user.objects.create_user(**validated_data)
        return user