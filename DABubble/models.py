from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AvatarModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    default_image_path = 'images/default.jpg' 

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
    createdFrom = models.CharField(max_length=250, blank=False, null=False)

class MessageModel(models.Model):
    channel = models.ForeignKey(ChannelModel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class PrivateChannelModel(models.Model):
    channelName = models.CharField(max_length=250, blank=False, null=False)
    channelDescription = models.CharField(max_length=250, blank=False, null=False)
    createdFrom = models.CharField(max_length=250, blank=False, null=False)
    channelMembers = models.ManyToManyField(User, related_name="private_channels")
