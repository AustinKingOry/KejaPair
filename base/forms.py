from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Home, Guest,Review
# from django.contrib.auth.models import user

class MyUserCreationForm(UserCreationForm):
    class Meta:
        # model = Profile
        model = User
        # fields = '__all__'
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'phone', 'category', 'bio', 'age', 'gender', 'location', 'profilePhoto']
        # fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'category', 'password1', 'password2']
        # exclude = ['id','UID','password','last_login','is_superuser','is_staff','is_active','date_joined','last_login','photosDir','interests','data_confirmed','verified','target_met','valid']

class GuestForm(ModelForm):
    class Meta:
        model = Guest
        fields = ['budget','moving_date']
        # exclude = ['num','homeId','host','available','likesCount','valid','verified','created','updated','photosDir']

class RoomForm(ModelForm):
    class Meta:
        model = Home
        fields = '__all__'
        exclude = ['num','homeId','host','available','likesCount','valid','verified','created','updated','photosDir']
        
class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['body','rating']