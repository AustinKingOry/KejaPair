from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q


def get_file_path(parentFolder,itemFolder):
    new_path = str(parentFolder+'/'+itemFolder)
    return new_path

def upload_path_handler(instance, filename):
    return "uploads/user_{id}/{file}".format(id=instance.id, file=filename)
def upload_path_handler_up(instance, filename):
    return "uploads/user_{id}/{file}".format(id=instance.user.id, file=filename)
def upload_path_handler_room(instance, filename):
    return "uploads/user_{id}/{file}".format(id=instance.host.id, file=filename)

class Hobby(models.Model):
    hbId = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-name', '-created']

    def __str__(self):
        return self.name
    def field_id(self):
        return self.hbId
    
class UserPhoto(models.Model):
    photoId = models.CharField(max_length=10)
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
    UID = models.CharField(max_length=11)
    hobbies = models.ManyToManyField(Hobby, related_name='hobbies', blank=True)
    pairs = models.ManyToManyField('PairRequest', related_name='pairs', blank=True)
    matches = models.ManyToManyField('Match', related_name='matches', blank=True)
    phone = models.CharField(max_length=15)
    category = models.CharField(default='Host', max_length=50)
    bio = models.TextField(null=True,blank=True)
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=50)
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
    # def full_name(self) -> str:
    #     return str(self.first_name)+" "+str(self.last_name)
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

class Guest(models.Model):
    guestId = models.CharField(max_length=10)
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
    photoId = models.CharField(max_length=10)
    host = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    room = models.ForeignKey('Home',on_delete=models.CASCADE,null=True)
    image = models.ImageField(null=False,blank=False,upload_to=upload_path_handler_room)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(null=False,default='room',max_length=200)
    description = models.TextField(null=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.photoId
    def field_id(self):
        return self.photoId

class Home(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    homeId = models.CharField(max_length=10)
    host = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='home_host')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    location = models.CharField(max_length=200)
    rent = models.IntegerField()
    security_deposit = models.IntegerField()
    bills_included = models.BooleanField(default=False)
    maps_link = models.URLField(null=True,blank=True, max_length=200)
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
        return self.homeId
    

class PairRequest(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    rqstId = models.CharField(max_length=10)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='pr_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='pr_searching')
    trigger = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='initiator')
    home = models.ForeignKey(Home,null=False,on_delete=models.CASCADE)
    status = models.CharField(null=False,max_length=20)
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.rqstId
    def field_id(self):
        return self.rqstId
    
class Match(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    matchId = models.CharField(max_length=10)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='Match_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='Match_searching')
    home = models.ForeignKey(Home,null=False,on_delete=models.CASCADE)
    matchType = models.CharField(null=False,max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.matchId
    def field_id(self):
        return self.matchId
    
class Like(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    likeId = models.CharField(max_length=10)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='receiver')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='sender')
    home = models.ForeignKey(Home,null=False,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.likeId
    def field_id(self):
        return self.likeId
    
    
class Review(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    reviewId = models.CharField(max_length=10)
    host = models.ForeignKey(User,on_delete=models.CASCADE,related_name='User')
    guest = models.ForeignKey(User,on_delete=models.CASCADE,related_name='participant')
    home = models.ForeignKey(Home,on_delete=models.CASCADE)
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
    num = models.IntegerField(default=1,auto_created=True)
    loginId = models.CharField(max_length=10)
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
    num = models.IntegerField(default=1,auto_created=True)
    notifId = models.CharField(max_length=10)
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
    num = models.IntegerField(default=1,auto_created=True)
    mailId = models.CharField(max_length=10)
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
    num = models.IntegerField(default=1,auto_created=True)
    cmId = models.CharField(max_length=10)
    host = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='cm_hosting')
    guest = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='cm_searching')
    home = models.ForeignKey(Home,null=False,on_delete=models.CASCADE)
    # matchType = models.CharField(null=False,max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cmId
    def field_id(self):
        return self.cmId
    
class PwdReset(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    resetId = models.CharField(max_length=10)
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
    num = models.IntegerField(default=1,auto_created=True)
    actId = models.CharField(max_length=10)
    trigger = models.ForeignKey(User,null=False,on_delete=models.CASCADE)
    target_id = models.CharField(null=True,max_length=10)
    activity_type = models.CharField(max_length=20,null=False)
    created = models.DateTimeField(auto_now_add=True)
    default_text = models.TextField(null=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.default_text
    def field_id(self):
        return self.actId