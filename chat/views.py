from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from chat.models import Thread,Chat
from base.models import User
from base.basicFunctions import encrypt_text,decrypt_text
from django.db.models import Q
from django.contrib import messages
from django import template

# Create your views here.

@login_required(login_url='signin')
def chats(request):
    
    # for thread in Thread.objects.all():
    #     thread.delete()
    # for chat in Chat.objects.all():
    #     chat.delete()
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chat_thread').order_by('-updated','-timestamp')
    thread_count = threads.count()
    u = request.GET.get('u') if request.GET.get('u') != None else ''
    if u !='':
        if User.objects.get(id=u) == request.user:
            u=''
            # messages.error(request,'you cannot message yourself')
            return redirect('/chats')
        else:
            receiver = User.objects.get(id=u)
            p1p2 = Thread.objects.filter(first_person=receiver,second_person=request.user).exists()
            p2p1 = Thread.objects.filter(first_person=request.user,second_person=receiver).exists()
            if p1p2 or p2p1:
                thread_exists = True
            else:
                thread_exists = False
    else:
        receiver=''
        thread_exists = False
        
    context = {'Threads':threads,
               'thread_count':thread_count,
               'receiver':receiver,
               'no_footer':True,
               'thread_exists':thread_exists,
               }
    return render(request,'chat/chat.html',context)