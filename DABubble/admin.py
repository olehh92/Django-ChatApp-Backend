from django.contrib import admin

from .models import ChannelModel
# Register your models here.

class ChannelAdmin(admin.ModelAdmin):
    field = ("channelname", "channelDescription", "createdFrom")
    list_display = ("channelname", "channelDescription", "createdFrom")

admin.site.register(ChannelModel)