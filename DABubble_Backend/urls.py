"""
URL configuration for DABubble_Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
    
Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
    
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    
"""
from django.contrib import admin
from django.urls import path, include, re_path
from DABubble.views import (LoginView, LogoutView, AvatarModelViewSet, AvatarUserModelView, 
                            PasswordRequestView, PasswordResetConfirm, RegistrationView, ChannelView, 
                            SingleChannelView, MessageEmojiView, MessageView, ThreadMessageView, ThreadEmojiView, 
                            UsersView, ActiveUserView)
from django.conf import settings
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.static import serve
from django.http import HttpResponseRedirect
import os

router = DefaultRouter()
router.register(r'images', AvatarModelViewSet, basename='image')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/', include(router.urls)),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:id>/', UsersView.as_view(), name='user-detail'),
    path('user/', ActiveUserView.as_view(), name='user'),
    path('activeUserImage/', AvatarUserModelView.as_view(), name='activeUserImage'),
    
    # Channel URLs
    path('channel/', ChannelView.as_view(), name='channel-list'),
    path('channel/<int:channel_id>/', SingleChannelView.as_view(), name='channel-detail'),

    # Message URLs
    path('channel/<int:channel_id>/messages/', MessageView.as_view(), name='message-list'),
    path('channel/<int:channel_id>/messages/<int:message_id>/', MessageView.as_view(), name='message-detail'),
    path('channel/<int:channel_id>/messages/<int:message_id>/emoji/', MessageEmojiView.as_view(), name='messageEmoji'),
    
    # Thread Message URLs
    path('channelThread/<int:thread_channel_id>/messages/', ThreadMessageView.as_view(), name='messageThread-list'),
    path('channelThread/<int:thread_channel_id>/messages/<int:message_id>/', ThreadMessageView.as_view(), name='messageThread-detail'),
    path('channelThread/<int:thread_channel_id>/messages/<int:message_id>/emoji/', ThreadEmojiView.as_view(), name='messageThreadEmoji'),

    # password reset
    path('password_reset/', PasswordRequestView.as_view(), name='password_reset'),  
    path('password_reset_confirm/', PasswordResetConfirm.as_view(), name='password_resetConfirm'),  
    
    #documentation
    re_path(r'^docu/$', lambda request: HttpResponseRedirect('/docu/index.html')),

    re_path(r'^docu/(?P<path>.*)$', serve, {
        'document_root': os.path.join(os.path.dirname(__file__), '../_build/html/'),
        'show_indexes': True,
    }),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns