import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from base.consumers import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeChat.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http":application,
    'websocket':AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/(?P<id>\d+)/$', PersonalChatConsumer.as_asgi()),

            # re_path(r'ws/group-chat/(?P<group_id>\d+)/$', GroupChatConsumer.as_asgi()),
        ])
    )
})
