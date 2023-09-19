from django.urls import path
from chat import consumers


websocket_urlpatterns = [
    path('chats/', consumers.ChatConsumer.as_asgi()),
    path('chat-seen/', consumers.ChatSeenConsumer.as_asgi()),
]