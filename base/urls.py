from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('profiles/<str:pk>/',views.profiles,name='profiles'),
    path('users/',views.users,name='users'),
    path('hosts/',views.hosts,name='hosts'),
    path('guests-listing/',views.guests_listing,name='guests-listing'),
    path('edit-profile/',views.updateUser,name='edit-profile'),
    path('add-activity/',views.newUserPhoto,name='add-activity'),
    path('guest-settings/',views.guest_settings,name='guest-settings'),
    path('signup/',views.signUp,name='signup'),
    path('signin/',views.signin,name='signin'),
    path('logout/',views.logoutUser,name='logout'),
    path('add-room/',views.createRoom,name='add-room'),
    path('rooms/',views.allRooms,name='all-room'),
    path('my-rooms/',views.myRooms,name='my-rooms'),
    path('host-rooms/<str:pk>/',views.userRooms,name='host-rooms'),
    path('add-room-photos/<str:pk>/',views.newRoomPhoto,name='add-room-photos'),
    path('edit-room/<str:pk>/',views.updateRoom,name='update-room'),
    path('pair-with/<str:pk>/',views.pair_with,name='pair-with'),
    path('my-pairs/',views.user_pairs,name='user-pairs'),
    path('manage-listing/',views.owner_chamber,name='owner-chamber'),
    path('room/<str:pk>/',views.room,name='room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-user/<str:pk>/', views.deleteUser, name="delete-user"),
    path('my-hobbies/', views.userhobbies, name="my-hobbies"),
    path('notifications/', views.user_notifications, name="notifications"),
    path('matches/', views.user_matches, name="my-matches"),
    path('match-with/<str:pk>/',views.match_with,name='match-with'),
    path('request-room/<str:pk>/',views.request_room,name='request-room'),
]
