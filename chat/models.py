from django.db import models
from base.models import User,Property
from django.db.models import Q

# Create your models here.

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']
        
        
        
class Chat(models.Model):
    num = models.IntegerField(default=1,auto_created=True)
    msgId = models.CharField(max_length=10)
    user = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='sending')
    # receiver = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name='receiving')
    property = models.ForeignKey(Property,null=True,on_delete=models.CASCADE)
    body = models.TextField(null=False)
    unread = models.BooleanField(default=True)
    receiverNotified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE,related_name='chat_thread')
    
    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.body[0:50]
    def field_id(self):
        return self.msgId