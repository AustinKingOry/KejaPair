from django.contrib import admin
from .models import Hobby,UserPhoto,RoomPhoto,User,Guest,Property,PairRequest,Match,Review,SignInLog,Notification,CompletedMatch,Like,Mail,PwdReset,ActivityLog
# Register your models here.

admin.site.register(Guest)
admin.site.register(Hobby)
admin.site.register(User)
admin.site.register(Property)
admin.site.register(UserPhoto)
admin.site.register(RoomPhoto)
admin.site.register(PairRequest)
admin.site.register(Match)
admin.site.register(Review)
admin.site.register(SignInLog)
admin.site.register(Notification)
admin.site.register(CompletedMatch)
admin.site.register(Like)
admin.site.register(Mail)
admin.site.register(PwdReset)
admin.site.register(ActivityLog)
