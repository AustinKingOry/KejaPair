import os
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.db.models import Q

from .models import User,Property as Room,Review,Guest,Like,RoomPhoto,UserPhoto,Hobby,Notification,PairRequest,ActivityLog as Log,Match
from chat.models import Chat,Thread
from .forms import MyUserCreationForm,RoomForm,GuestForm,ReviewForm
from .utils import createId,send_notification,pairable,create_pair,pair_exists,suggestPair,track_activity,createMatch,book_room,booked_rooms,get_activity_feed,map_model,activity_body

# Create your views here.
def home(request):
    rooms=Room.objects.all()
    room_count = rooms.count()
    profiles = User.objects.all()
    context = {'rooms':rooms,'users':profiles,'room_count':room_count}
    return render(request,'base/home.html',context)


def users(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'base/users.html', context)

def profiles(request, pk):
    user = User.objects.get(id=pk)
    property_activities = []
    profile_activities = []
    hobbies = user.hobbies.all()
    rooms = Room.objects.filter(host=user)
    feed_photos = user.photosList.all()
    rooms_photos = RoomPhoto.objects.filter(host=user)
    request_user = User.objects.filter(id=request.user.id)
    likes_rec = Like.objects.filter(guest=user)
    activities = get_activity_feed(user)[0:30]
    for activity in activities:
        target_model = map_model(str(activity.target_model))
        if target_model:
            try:
                item = target_model.objects.get(id=activity.target_id)
                activity.target_image_url = activity_body(item,activity)[0]
                activity.target_text = activity_body(item,activity)[1]
            except:
                item = None
            
        if str(activity.activity_group).lower()=='property':
            property_activities.append(activity)
        elif str(activity.activity_group).lower()=='profile':
            profile_activities.append(activity)
    # PairRequest.objects.all().delete()
    # Notification.objects.all().delete()
    # Like.objects.all().delete()
    if request_user.exists():
        can_pair=pairable(user,request.user)
        paired = pair_exists(user,request.user)
    else:
        can_pair=False
        paired = False
    context = {'profile': user,'hobbies': hobbies,'rooms':rooms,'feed_photos':feed_photos,'rooms_photos':rooms_photos,'pairable':can_pair,'pair_exists':paired,'likes_rec':likes_rec,'active_page':'profile','property_activities':property_activities,'profile_activities':profile_activities}
    return render(request, 'base/profile.html', context)

def hosts(request):
    hosts = User.objects.filter(category='Host')[0:80]
    request_user = User.objects.filter(id=request.user.id)
    if request.user.is_authenticated:
        user = request.user   
        #find a better alternative here
        all_hosts = user.pairs.values('host_id')
        pairs = []
        for i in all_hosts:
            pairs.append(i['host_id'])
    else:
        pairs = None
    context = {'hosts': hosts,'pairs':pairs}
    return render(request, 'base/hosts.html', context)

def guests_listing(request):
    guests = User.objects.filter(category='Guest')[0:80]
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)      
        #find a better alternative here too
        all_guests = user.pairs.values('guest_id')
        pairs = []
        for i in all_guests:
            pairs.append(i['guest_id'])
    else:
        pairs = None
    context = {'guests': guests,'pairs':pairs}
    return render(request, 'base/guests-listing.html', context)

def signUp(request):
    form = MyUserCreationForm()
    if(request.method == 'POST'):
        form = MyUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.UID = str(createId(User,User.UID,'PRF'))
            user.username = user.username.lower()
            user.save()
            messages.success(request,'welcome!')
            login(request, user)
            if request.POST.get('category') == 'Guest':
                return redirect('guest-settings')
            elif request.POST.get('category') == 'Host' or request.POST.get('category') == 'Owner':
                return redirect('add-room')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    context = {'form':form}
    return render(request,'base/signup.html',context)

@login_required(login_url='signin')
def guest_settings(request):
    user = request.user
    category = str(user.category).lower()
    if category == 'guest':
        cur_settings = user.guest_set.all()
        if(cur_settings):
            cur_settings = Guest.objects.get(userId=user)
            form = GuestForm(instance=cur_settings)
        else:
            form = GuestForm()
        if request.method == 'POST':
            form = GuestForm(request.POST)
            if form.is_valid():
                if Guest.objects.filter(userId=user).exists():
                    cur_settings.budget = request.POST.get('budget')
                    cur_settings.moving_date = request.POST.get('moving_date')
                    cur_settings.save()
                else:
                    guest = form.save(commit=False)
                    guest.guestId= str(createId(Guest,Guest.guestId,'GID'))
                    guest.userId= request.user                
                    guest.save()
                messages.success(request,'Account settings updated successfully!')
                return redirect('edit-profile')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        context = {'form':form,'guest':cur_settings,'active_page':'guest-settings'}
        return render(request,'base/guest-settings.html',context)
    else:
        return HttpResponse('Sorry, This page is only accessible to guest type accounts. Your account type is: '+category)

def signin(request):
    if(request.method=='POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'Account does not exist!')
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('/')
            # return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request,'Incorrect username/password combination!')
    context = {}
    return render(request,'base/signin.html',context)


@login_required(login_url='signin')
def updateUser(request):
    user = request.user
    form = MyUserCreationForm(instance=user)
    user_db = User.objects.get(id=user.id)
    hobbies = user_db.hobbies.all()
    hobbies_count = hobbies.count()
    category = user_db.category
    if category.lower()=='guest':
        guest_data = Guest.objects.filter(userId=user_db).first()
    else:
        guest_data = None
    if request.method == 'POST':
        # messages.success(request,'POST Detected!!')
        # form = MyUserCreationForm(request.POST, request.FILES,instance=user)
        # if form.is_valid():/        
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.bio = request.POST.get('bio')
        user.age = request.POST.get('age')
        user.location = request.POST.get('location')
        user.phone = request.POST.get('phone')
        # user.category = request.POST.get('category')
        # messages.success(request,'Form is valid!!')
        if(request.FILES):
            user.profilePhoto = request.FILES.get('profilePhoto')
        user.save()
        messages.success(request,'Profile updated successfully!')
        track_activity(
            user,
            'Profile Update',
            'Profile',
            str(user.get_full_name()) + ' updated their profile.',
            'user',
            user.id,
        )
        return redirect('edit-profile')
        # else:
        #     messages.error(request,form.errors)
    context = {'form': form,'active_page':'settings','hobbies':hobbies,'hobbies_count':hobbies_count,'guest_data':guest_data}
    return render(request, 'base/edit-profile.html',context)

@login_required(login_url='signin')
def newUserPhoto(request):
    user = request.user
    photos = user.photosList.all()
    if request.method == 'POST':
        if request.FILES:
            newRoomFile = request.FILES.getlist('image')
            
            photo_ids = []
            for image in newRoomFile:
                photo = UserPhoto.objects.create(
                    photoId = createId(UserPhoto,UserPhoto.photoId,'PHU'),
                    user = user,
                    image = image,
                    category = 'profile',
                    description = request.POST.get('description'),
                )
                user.photosList.add(photo)
                photo_ids.append(photo.id)
            
            track_activity(
                user,
                'New Photo',
                'Profile',
                '',
                'user_photo',
                user.id,
            )
            messages.info(request,'photos is uploaded!')
        return redirect('edit-profile')

    context = {'photos':photos}
    return render(request,'base/add-profile-photos.html',context)

@login_required(login_url='signin')
def pair_with(request,pk):
    user1= User.objects.get(id=pk)
    user2=request.user
    valid=False
    if user1.category == 'Host' and user2.category == 'Guest':
        if not Room.objects.filter(host=user1).exists():
            messages.error(request,"A valid room is required for you to be able to pair!")
            room=None
            valid=False
        else:
            room = Room.objects.get(host=user1)
            valid=True
        host= user1
        guest= user2
    elif user2.category == 'Host' and user1.category == 'Guest':
        if not Room.objects.filter(host=user2).exists():
            messages.error(request,"A valid room is required for you to be able to pair!")
            room=None
            valid=False
        else:
            room = Room.objects.get(host=user2)
            valid=True
        host= user2
        guest= user1
    else:
        messages.error(request,"An error occurred. Check your account details and try again!")
    if(valid):
        if pairable(user1,user2):
            pair = create_pair(host,guest,room,request.user)
            if pair==True:
                send_notification(
                    str(request.user.get_full_name())+' sent you a pair request. Get in touch with them to check your compatibility and start living together.',
                    'New Pair Request',
                    user2,
                    user1,
                    'Pairing',
                    "/profiles/"+str(request.user.id)
                )
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='signin')
def match_with(request,pk):
    user1= User.objects.get(id=pk)
    user2=request.user
    valid=False
    if user1.category == 'Host' and user2.category == 'Guest':
        if not Room.objects.filter(host=user1).exists():
            messages.error(request,"A valid room is required for you to be able to match!")
            room=None
        else:
            room = Room.objects.get(host=user1)
            valid=True
        host= user1
        guest= user2
    elif user2.category == 'Host' and user1.category == 'Guest':
        if not Room.objects.filter(host=user2).exists():
            messages.error(request,"A valid room is required for you to be able to match!")
            room=None
        else:
            room = Room.objects.get(host=user2)
            valid=True
        host= user2
        guest= user1
    else:
        messages.error(request,"An error occurred. Check your account and try again!")
    if(valid):
        createMatch(guest,host,room,user2)
    return redirect('my-matches')

@login_required(login_url='signin')
def request_room(request,pk):
    user2=request.user
    valid=False
    if not Room.objects.filter(id=pk).exists():
        messages.error(request,"The house/room that you requested does not exist!")
        room=None
    else:
        room = Room.objects.get(id=pk)
        user1= room.host
        if (user1.category).lower() == 'owner' and (user2.category).lower() == 'guest':
            valid=True
            host= user1
            guest= user2
        else:
            messages.error(request,"An error occurred. Check your account and try again!")
        if(valid):
            if book_room(guest,host,room):
                messages.success(request,'Request has been sent successfully. You will be contacted for updates😀.')
            else:
                messages.error(request,'We seem to be having trouble sending this request. Ensure that your data is up to date and try again😟.')
            
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='signin')
def user_pairs(request):
    request_user = User.objects.filter(id=request.user.id)
    if request_user.exists():
        user = request_user.first()
        #find a better alternative here
        pairs = user.pairs.all()
        sent_pairs_count=user.pairs.filter(trigger=user).count()
        received_pairs_count=pairs.count()-sent_pairs_count
        #use a better algorithm here instead of calling the function everytime a view is loaded
        reccommended_pairs=suggestPair(user.id)[0:30]
        reccommended_pairs_count=len(reccommended_pairs)
        try:
            guest_obj = Guest.objects.get(userId=user)
        except:
            guest_obj = None
        requested_rooms = booked_rooms(guest_obj)
        # messages.info(request,requested_rooms)
    else:
        pairs = None
        reccommended_pairs=None
        reccommended_pairs_count=0
        sent_pairs_count=0
        received_pairs_count=0
        requested_rooms = None
    context = {'pairs':pairs,'suggested_pairs':reccommended_pairs,'reccommended_pairs_count':reccommended_pairs_count,'sent_pairs_count':sent_pairs_count,'received_pairs_count':received_pairs_count,'active_page':'pairs','booked_rooms':requested_rooms}
    return render(request, 'base/user-pairs.html', context)

@login_required(login_url='signin')
def user_matches(request):
    request_user = User.objects.filter(id=request.user.id)
    
    if request_user.exists():
        user = request_user.first()
        #find a better alternative here
        matches = Match.objects.filter(
            Q(host=user)|
            Q(guest=user)
        )[0:10]
        matches_count=matches.count()
    else:
        matches = None
        matches_count = 0
    context = {'matches':matches,'matches_count':matches_count,'active_page':'matches'}
    return render(request, 'base/user-matches.html', context)

def logoutUser(request):
    logout(request)
    # return redirect('home')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='signin')
def deleteUser(request, pk):
    user = User.objects.get(id=pk)

    if request.user != user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        user.delete()
        messages.success(request,'The account has been deleted successfully.')
        return redirect('logout')
    context = {'obj': user}
    return render(request, 'base/delete.html', context)

@login_required(login_url='signin')
def user_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)[0:80]
    unread_count = Notification.objects.filter(user=user,seen=False).count()
    read_count = Notification.objects.filter(user=user,seen=True).count()
    
    # this section of code is a ticking time-bomb for large datasets
    #use SELECT DISTINCT equivalent code to do the same
    all_notifs = Notification.objects.all()
    categories = []
    for n in all_notifs:
        cur_n=n.notifType
        if cur_n not in categories:
            categories.append(cur_n)
    # end of time-bomb        
    context = {'notifications':notifications,'unread_count':unread_count,'read_count':read_count,'categories':categories,'active_page':'notif'}
    return render(request,'base/notifications.html',context)

@login_required(login_url='signin')
def userhobbies(request):
    user = request.user
    hobbies = user.hobbies.all()  
    allhobbies = Hobby.objects.all()[0:80]
    context = {'hobbies':hobbies,'all_hobbies':allhobbies}
    return render(request,'base/user-hobbies.html',context)

@login_required(login_url='signin')
def createRoom(request):
    existing_rooms = Room.objects.filter(host=request.user)    
    if (request.user.category).lower() == 'guest':
        context={'form':None}
        messages.error(request,'Your account does not have access to this section.')
    elif request.user.category=='Host' and existing_rooms.count() >= 1:
        context = {}
        messages.error(request,'You have reached your maximum number of rooms to upload!')
    else:
        form = RoomForm()
        if request.method == 'POST':
            form = RoomForm(request.POST,request.FILES)
            if form.is_valid():       
                room = form.save(commit=False)
                room.propertyId = str(createId(Room,Room.propertyId,'RM'))
                room.host = request.user
                room.save()
                messages.success(request,'Your room has been added successfully!!')
                track_activity(
                    request.user,
                    'New Property',
                    'Property',
                    str(request.user.get_full_name()) + ' added a new property.',
                    'property',
                    room.id,
                )
                return redirect('home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        context = {'form':form,'active_page':'add-room'}
    return render(request,'base/add-room.html',context)

@login_required(login_url='signin')
def newRoomPhoto(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    photos = room.photosList.all()
    if request.method == 'POST':
        if request.FILES:
            newRoomFile = request.FILES.getlist('new-photo-input')
            newRoomDescription = request.POST.getlist('description')
            loopcounter = 0
            photo_ids = []
            for image in newRoomFile:
                photo = RoomPhoto.objects.create(
                    photoId = createId(RoomPhoto,RoomPhoto.photoId,'PHR'),
                    host = room.host,
                    room = room,
                    image = image,
                    category = 'room',
                    description = newRoomDescription[loopcounter],
                )
                room.photosList.add(photo)
                photo_ids.append(photo.id)
                loopcounter+=1
            track_activity(
                request.user,
                'New Property Photo',
                'Property',
                str(request.user.get_full_name()) + ' added a new photo to their room.',
                'property',
                room.id,
            )
            messages.info(request,'Post created sucessfully!')
    context = {'room':room,'photos':photos}
    return render(request,'base/add-room-photos.html',context)

def allRooms(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms = Room.objects.filter(location__icontains=q)
    rooms = Room.objects.filter(
        Q(rent__icontains=q) |
        Q(location__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # rooms=Room.objects.all()
    room_count = rooms.count()
    # profiles = User.objects.all()
    # context = {'rooms':rooms,'users':profiles}
    context = {'rooms':rooms,'room_count':room_count}
    return render(request,'base/rooms.html',context)

@login_required(login_url='signin')
def myRooms(request):
    host=request.user
    rooms=Room.objects.filter(host=request.user)
    room_count = rooms.count()
    context = {'rooms':rooms,'room_count':room_count,'host':host,'active_page':'listing'}
    return render(request,'base/user-rooms.html',context)

@login_required(login_url='signin')
def owner_chamber(request):
    host=request.user
    rooms=Room.objects.filter(host=request.user)
    room_count = rooms.count()
    context = {'rooms':rooms,'room_count':room_count,'host':host,'active_page':'owner-chamber'}
    return render(request,'base/owners-chamber.html',context)

def userRooms(request,pk):
    host = User.objects.get(id=pk)
    rooms=Room.objects.filter(host=host)
    room_count = rooms.count()
    context = {'rooms':rooms,'room_count':room_count,'host':host}
    return render(request,'base/user-rooms.html',context)

def room(request, pk):
    if Room.objects.filter(id=pk).exists():
        room = Room.objects.get(id=pk)
        host_id=room.host.id
        if User.objects.filter(id=host_id).exists():
            host = User.objects.get(id=host_id)
            reviews = Review.objects.filter(host=host)
            reviews_count = reviews.count()
            reviewForm = ReviewForm()
            photos = room.photosList.all()
            if request.user.is_authenticated:
                user_likes = Like.objects.filter(guest=request.user,property=room).exists()
            else:
                user_likes = False
                
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.reviewId=createId(Review,Review.reviewId,'RVW')
                    review.host = room.host
                    review.guest = request.user
                    review.property = room
                    review.save()
                    
                    send_notification(
                        str(request.user.get_full_name())+' added a new review for you on one of your listings: '+'"'+str(request.POST.get('body'))+'"',
                        'New Review',
                        request.user,
                        host,
                        'Review',
                        "/room/"+str(room.id)+"/#reviews"
                    )
                    track_activity(
                        request.user,
                        'Profile Update',
                        'Property',
                        f"{str(request.user.get_full_name())}  posted a review to {host.get_full_name()}.",
                        'review',
                        review.id,
                    )
                else:                    
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"Error in {field}: {error}")
            
            hobbies = room.host.hobbies.all()
            hobbies_count = hobbies.count()
            request_user = User.objects.filter(id=request.user.id)
            if request_user.exists():
                can_pair=pairable(host,request.user)
                paired = pair_exists(host,request.user)
            else:
                can_pair=False
                paired=False
            context = {'room': room, 'reviews': reviews,'reviews_count':reviews_count,'hobbies': hobbies,'hobbies_count':hobbies_count,'user_likes':user_likes,'photos':photos,'reviewForm':reviewForm,'pairable':can_pair,'pair_exists':paired}
        else:
            messages.error(request,'This user account does not exist or has been deleted!')
            return redirect('home')
    else:
        room=None
        host_id=None
        messages.error(request,'This room does not exist or has been deleted!')
        return redirect('home')
    
    return render(request, 'base/room.html', context)

@login_required(login_url='signin')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    photos = room.photosList.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST,request.FILES)
        if form.is_valid():
            room.name = request.POST.get('name')
            room.description = request.POST.get('description')
            room.location = request.POST.get('location')
            room.capacity = request.POST.get('capacity')
            room.occupants = request.POST.get('occupants')
            room.preferredGender = request.POST.get('preferredGender')
            room.rent = request.POST.get('rent')
            room.security_deposit = request.POST.get('security_deposit')
            room.maps_link = request.POST.get('maps_link')
            if request.FILES:
                room.coverPhoto = request.FILES.get('coverPhoto')
            if(request.POST.get('bills_included')):                
                if(request.POST.get('bills_included').lower()=='true'):
                    room.bills_included = True
                else:
                    room.bills_included = False
            room.save()
            messages.success(request,'Your room was updated successfully 😉.')
            return redirect(request.META['HTTP_REFERER'])
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    context = {'form': form, 'room': room,'photos':photos}
    return render(request, 'base/edit-room.html', context)

@login_required(login_url='signin')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        messages.success(request,'The room has been deleted successfully.')
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)


# @login_required(login_url='signin')
# def chats(request):
#     threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
#     thread_count = threads.count
#     u = request.GET.get('u') if request.GET.get('u') != None else ''
#     # user=request.user
#     # chats = Chat.objects.filter(user=user)
#     if u !='':
#         receiver = User.objects.get(id=u)
#         p1p2 = Thread.objects.filter(first_person=receiver,second_person=request.user).exists()
#         p2p1 = Thread.objects.filter(first_person=request.user,second_person=receiver).exists()
#         if p1p2 or p2p1:
#             thread_exists = True
#         else:
#             thread_exists = False
#     else:
#         receiver=''
#         thread_exists = False
        
#     # if request.method == 'POST':
#     #     Chat.objects.create(
#     #         msg = request.POST.get('msg-input'),
#     #         sender = request.user,
#     #         receiver = User.objects.get(id=request.POST.get('target')),
#     #         msgId = createId(Chat,Chat.msgId,'MSG'),
#     #         seen = False,
#     #         receiverNotified = False,
#     #     )
        
#     context = {'Threads':threads,
#                'thread_count':thread_count,
#                'receiver':receiver,
#                'no_footer':True,
#                'thread_exists':thread_exists,
#                }
#     return render(request,'base/chat.html',context)