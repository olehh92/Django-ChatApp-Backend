from django.contrib import admin

from .models import ChannelModel, ThreadChannelModel, MessageModel
# Register your models here.

class ChannelAdmin(admin.ModelAdmin):
    field = ("channelname", "channelDescription", "createdFrom")
    list_display = ("channelname", "channelDescription", "createdFrom")

admin.site.register(ChannelModel)

class ChannelAdmin(admin.ModelAdmin):
    field = ("channelname", "channelDescription", "createdFrom")
    list_display = ("channelname", "channelDescription", "createdFrom")

admin.site.register(ThreadChannelModel)

class ChannelAdmin(admin.ModelAdmin):
    field = ("id", "content", "sender")
    list_display = ("id", "content", "sender")

admin.site.register(MessageModel)