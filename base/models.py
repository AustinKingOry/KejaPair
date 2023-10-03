from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver


def get_file_path(parentFolder,itemFolder):
    new_path = str(parentFolder+'/'+itemFolder)
    return new_path

def upload_path_handler(instance, filename):
    return "uploads/user_{id}/{file}".format(id=instance.id, file=filename)
def upload_path_handler_up(instance, filename):
    return "uploads/user_{id}/post_{pid}/{file}".format(id=instance.user.id,pid=instance.id, file=filename)
def upload_path_handler_room(instance, filename):
    return "uploads/user_{id}/prp_{pid}/{file}".format(id=instance.host.id,pid=instance.id,file=filename)
def upload_path_handler_room_new(instance, filename):
    return "uploads/user_{id}/prp_{pid}/{file}".format(id=instance.host.id,pid=instance.room.id,file=filename)

class Hobby(models.Model):
    hbId = models.CharField(max_length=10,unique=True)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-name', '-created']

    def __str__(self):
        return self.name
    def field_id(self):
        return self.hbId
    
class UserPhoto(models.Model):
    photoId = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True,related_name='photo_user')
    image = models.ImageField(null=False,blank=False,upload_to=upload_path_handler_up)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(null=False,default='user',max_length=200)
    description = models.TextField(null=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.photoId
    def field_id(self):
        return self.photoId


class User(AbstractUser):
    gender_1 = 'Male'
    gender_2 = 'Female'
    gender_3 = 'Other'
    gender_choices = [
        (gender_1,'Male'),
        (gender_2,'Female'),
        (gender_3,'Other'),
        ]
    type_1 = 'Host'
    type_2 = 'Owner'
    type_3 = 'Guest'
    account_types = [
        (type_1,"I have a house/room and I'm looking for a roommate."),
        (type_2,"I'm a property owner looking for tenants."),
        (type_3,"I'm looking for a place to stay."),
    ]
    UID = models.CharField(max_length=11,unique=True)
    hobbies = models.ManyToManyField(Hobby, related_name='hobbies', blank=True)
    pairs = models.ManyToManyField('PairRequest', related_name='pairs', blank=True)
    matches = models.ManyToManyField('Match', related_name='matches', blank=True)
    phone = models.CharField(max_length=15)
    category = models.CharField(max_length=50,choices=account_types,default=type_1)
    bio = models.TextField(null=True,blank=True,default='No bio.')
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=50,choices=gender_choices,default=gender_1)
    location = models.CharField(max_length=200)
    profilePhoto = models.ImageField(upload_to=upload_path_handler,default='avatar.png')
    photosList = models.ManyToManyField(UserPhoto,related_name='timeline_photos',blank=True)
    data_confirmed = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    target_met = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.username
    def field_id(self):
        return self.UID
    def delete(self, *args, **kwargs):
        # Delete associated photos and their image files
        self.profilePhoto.delete()
        for photo in self.photosList.all():
            photo.image.delete()
            photo.delete()

        super().delete(*args, **kwargs)
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

class Guest(models.Model):
    guestId = models.CharField(max_length=10,unique=True)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    budget = models.IntegerField(null=True,default=0)
    cleared = models.BooleanField(default=False)
    moving_date = models.DateField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self) -> str:
        return self.guestId
    def field_id(self):
        return self.guestId
      
class RoomPhoto(models.Model):
    photoId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    room = models.ForeignKey('Property',on_delete=models.CASCADE,null=True)
    image = models.ImageField(null=False,blank=False,upload_to=upload_path_handler_room_new)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(null=False,default='room',max_length=200)
    description = models.TextField(null=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.photoId
    def field_id(self):
        return self.photoId

class Property(models.Model):
    propertyId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='property_host')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    location = models.CharField(max_length=200)
    rent = models.IntegerField()
    security_deposit = models.IntegerField()
    bills_included = models.BooleanField(default=False)
    maps_link = models.CharField(null=True,blank=True, max_length=200,help_text="You may need to allow access to your location to access maps navigation.")
    capacity = models.IntegerField(default=1)
    occupants = models.IntegerField(default=0)
    preferredGender = models.CharField(default="Not Necessary",max_length=50)
    available = models.BooleanField(default=True)
    coverPhoto = models.ImageField(upload_to=upload_path_handler_room, max_length=None,default='house-avatar.svg')
    photosList = models.ManyToManyField(RoomPhoto,related_name='room_photos',blank=True)
    requestsList = models.ManyToManyField(Guest,related_name='room_requesters',blank=True)
    likesCount = models.IntegerField(default=0)
    valid = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['updated', 'created']

    def __str__(self):
        return self.name
    def field_id(self):
        return self.propertyId
    def delete(self, *args, **kwargs):
        # Delete associated photos and their image files
        self.coverPhoto.delete()
        for photo in self.photosList.all():
            photo.image.delete()
            photo.delete()

        super().delete(*args, **kwargs)

class PairRequest(models.Model):
    rqstId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='pr_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='pr_searching')
    trigger = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='initiator')
    property = models.ForeignKey(Property,null=False,on_delete=models.CASCADE)
    status = models.CharField(null=False,max_length=20)
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.rqstId
    def field_id(self):
        return self.rqstId
    
class Match(models.Model):
    matchId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='Match_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='Match_searching')
    property = models.ForeignKey(Property,null=False,on_delete=models.CASCADE)
    matchType = models.CharField(null=False,max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.matchId
    def field_id(self):
        return self.matchId
    
class Like(models.Model):
    likeId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='receiver')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='sender')
    property = models.ForeignKey(Property,null=False,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.likeId
    def field_id(self):
        return self.likeId
    
    
class Review(models.Model):
    reviewId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,on_delete=models.CASCADE,related_name='User')
    guest = models.ForeignKey(User,on_delete=models.CASCADE,related_name='participant')
    property = models.ForeignKey(Property,on_delete=models.CASCADE)
    body = models.TextField(null=False)
    rating = models.IntegerField(null=False,default=1)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.body
    def field_id(self):
        return self.reviewId
    
class SignInLog(models.Model):
    loginId = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(User,null=False,on_delete=models.CASCADE)
    username = models.CharField(max_length=200)
    device = models.TextField(null=False)
    location = models.CharField(null=False,default='Unspecified',max_length=100)
    success = models.BooleanField(null=False,default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    def field_id(self):
        return self.loginId
    
class Notification(models.Model):
    notifId = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name="Target_User")
    trigger_user = models.ForeignKey(User,null=True,on_delete=models.CASCADE,related_name='Trigger_User')
    notifType = models.CharField(null=False,max_length=20)
    body = models.TextField(null=False)
    title = models.CharField(max_length=200,null=True)
    link = models.CharField(null=False,max_length=800)
    seen = models.BooleanField(null=False,default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.body[0:50]
    def field_id(self):
        return self.notifId
    
class Mail(models.Model):
    mailId = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(User,null=False,on_delete=models.CASCADE)
    userMail = models.EmailField(null=False)
    mailSubject = models.CharField(null=False,max_length=200)
    body = models.TextField(null=False)
    sent = models.BooleanField(null=False,default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
    def field_id(self):
        return self.mailId
    
class CompletedMatch(models.Model):
    cmId = models.CharField(max_length=10,unique=True)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='cm_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='cm_searching')
    property = models.ForeignKey(Property,null=False,on_delete=models.CASCADE)
    # matchType = models.CharField(null=False,max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cmId
    def field_id(self):
        return self.cmId
    
class PwdReset(models.Model):
    resetId = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(User,null=False,on_delete=models.CASCADE)
    pwdToken = models.TextField(null=False)
    pwdToken = models.TextField(null=False)
    expires = models.DateTimeField(null=False)
    email = models.EmailField(null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    def field_id(self):
        return self.resetId

class ActivityLog(models.Model):
    rec_id = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=255,default='')
    activity_group = models.CharField(max_length=255,default='')
    activity_details = models.TextField(null=True,blank=True)
    target_model = models.CharField(max_length=255,default='')  # Store model identifier/keyword
    target_id = models.PositiveIntegerField(default=0)  # Store the related model instance ID
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.rec_id
    def field_id(self):
        return self.rec_id
