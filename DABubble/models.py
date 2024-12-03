# models.py

from django.db import models
from django.contrib.auth.models import User

class AvatarModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    default_image_path = 'assets/img/avatar/avatar_empty.svg' 

    def save(self, *args, **kwargs):
        if not self.image and not self.image_path:
            self.image_path = self.default_image_path
        super().save(*args, **kwargs)

    def __str__(self):
        return self.image.name if self.image else self.image_path

class ChannelModel(models.Model):
    channelName = models.CharField(max_length=250, blank=False, null=False)
    channelDescription = models.CharField(max_length=250, blank=False, null=False)
    channelMembers = models.ManyToManyField(User, related_name="channels")
    createdFrom = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_channels")
    privateChannel = models.BooleanField(default=False)

    def __str__(self):
        return self.channelName

class MessageModel(models.Model):
    channel = models.ForeignKey(ChannelModel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    threadOpen = models.BooleanField(default=False)
    thread_channel = models.ForeignKey('ThreadChannelModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    emoji_handsup = models.ManyToManyField(User, related_name='emoji_handsup', blank=True)
    emoji_check = models.ManyToManyField(User, related_name='emoji_check', blank=True)
    emoji_nerd = models.ManyToManyField(User, related_name='emoji_nerd', blank=True)
    emoji_rocket = models.ManyToManyField(User, related_name='emoji_rocket', blank=True)
    messageData = models.FileField(upload_to='ulpoads/', null=True, blank=True)
    def __str__(self):
        return f'{self.sender} - {self.content[:20]}'

class ThreadChannelModel(models.Model):
    threadName = models.CharField(max_length=250, blank=False, null=False)
    threadDescription = models.CharField(max_length=250, blank=False, null=False)
    mainChannel = models.ForeignKey(ChannelModel, on_delete=models.CASCADE, related_name='thread_channels')
    createdFrom = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_threads")
    threadMember = models.ManyToManyField(User, related_name="threads")
    original_message = models.ForeignKey(MessageModel, on_delete=models.CASCADE, related_name='threads')

    def __str__(self):
        return f'{self.threadName} - {self.mainChannel.channelName}'

class ThreadMessageModel(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    thread_channel = models.ForeignKey('ThreadChannelModel', on_delete=models.CASCADE, related_name='thread_messages')
    emoji_handsup = models.ManyToManyField(User, related_name='emoji_handsup_thread', blank=True)
    emoji_check = models.ManyToManyField(User, related_name='emoji_check_thread', blank=True)
    emoji_nerd = models.ManyToManyField(User, related_name='emoji_nerd_thread', blank=True)
    emoji_rocket = models.ManyToManyField(User, related_name='emoji_rocket_thread', blank=True)
    messageData = models.FileField(upload_to='ulpoads/', null=True, blank=True)
    def __str__(self):
        return f'{self.sender} - {self.content[:20]}'
    
