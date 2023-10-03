from django.urls import path
from . import consumers as baseConsumers
from chat import consumers as chatConsumers


websocket_urlpatterns = [
    path('room/room-likes-handler/', baseConsumers.RoomLikesConsumer.as_asgi()),    
    path('hobbies-handler/', baseConsumers.NewHobbiesConsumer.as_asgi()),  
    path('handle-photo/', baseConsumers.HandlePhotosConsumer.as_asgi()),
    path('clear-notification/', baseConsumers.ClearNotificationConsumer.as_asgi()),
    path('live-updates/', baseConsumers.LiveDataConsumer.as_asgi()),
    path('delete-room/', baseConsumers.PropertyConsumer.as_asgi()),
    path('remove-listing/', baseConsumers.RemoveListingConsumer.as_asgi()),
    
    path('chats/', chatConsumers.ChatConsumer.as_asgi()),
    path('chat-seen/', chatConsumers.ChatSeenConsumer.as_asgi()),
]