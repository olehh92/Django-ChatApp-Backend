from django.contrib import admin

from .models import ChannelModel, PrivateChannelModel
# Register your models here.

class ChannelAdmin(admin.ModelAdmin):
    field = ("channelname", "channelDescription", "createdFrom")
    list_display = ("channelname", "channelDescription", "createdFrom")

admin.site.register(ChannelModel)

class ChannelAdmin(admin.ModelAdmin):
    field = ("channelname", "channelDescription", "createdFrom", "channelMembers")
    list_display = ("channelname", "channelDescription", "createdFrom", "channelMembers")
    
admin.site.register(PrivateChannelModel)