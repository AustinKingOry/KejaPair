from django.urls import path
from . import views
urlpatterns = [
    path('', views.chats),
    path('chats/', views.chats, name="chats"),
]
