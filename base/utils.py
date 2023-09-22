from .models import Notification,User,PairRequest,Property as Room,Guest,ActivityLog as Log,Match
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import re

def encrypt_text(key, text):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_text = pad(text.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    encrypted_text = b64encode(encrypted_bytes).decode('utf-8')
    return encrypted_text

def decrypt_text(key, encrypted_text):
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_bytes = b64decode(encrypted_text)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    decrypted_text = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
    return decrypted_text

def RemovePrefix(index,prefix):
    s=str(index)
    if s !='':
        if prefix in str(s):
            res = int(str(s).replace(prefix,''))
        else:
            res = int(re.search(r'\d+', s).group())
    else:
        res = 1
    return res

def addPrefix(prefix,index):
    if (index<10):
        res= str(prefix)+"00"+str(index)
        return res

    elif(index>=10):
        res = str(prefix)+"0"+str(index)
        return res

def createId(table,fieldname,prefix)->str:
    '''
    Creates unique id values for objects in the database, by checking and incrementing the integer part of the field with the highest value.

    @param `table` - name of class or table as stored in database
    @param `preffix` - the preceeding initials that are constant for all fields

    e.g `createId(User,'USID')` checks the integer part of the highest `UID` and returns `USID001` if the table was empty.

    '''
    fieldname = str(fieldname)
    idsArray = [0]
    if table.objects.all().count() > 0:
        tableFields = table.objects.latest('created')
        idsArray.append(tableFields.field_id())
    else:
        tableFields = None

    idPrefix=prefix
    dm_adms = [0]
    for field in idsArray:
        newRow = field
        index = RemovePrefix(newRow,idPrefix)
        newRow = int(index)
        dm_adms.append(newRow)
    
    cur_max = max(dm_adms)
    
    if not cur_max==1:
        newId =cur_max+1
        index1 = addPrefix(idPrefix,newId)
        newId = index1
    else:
        newId =cur_max+1
        index1 = addPrefix(idPrefix,newId)
        newId = index1

    return newId

def same_user(u1,u2):
    res = False
    if User.objects.filter(id=u1.id).exists() and User.objects.filter(id=u2.id).exists():
        if u1.id==u2.id:
            res = True
    return res
        

def send_notification(message,title,trigger,target,type,link):
    msg = message
    user = target
    trigger = trigger
    notif_type = type
    notif_link = link
    notif_title = title
    
    notification = Notification.objects.create(
        notifId = createId(Notification,Notification.notifId,'NTF'),
        user=user,
        trigger_user = trigger,
        notifType = notif_type,
        link = notif_link,
        body = msg,
        title = notif_title,
        seen = False
    )
    
    if(notification):
        return True
    else:
        return False
    
def clear_notification(id,user):
    notif_id = id
    notif = Notification.objects.get(id=notif_id,user=user)
    notif.seen = True
    status=notif.save()
    return status

 
def pairable(host,guest):
    pr = False
    u1 = User.objects.get(id=host.id)
    u2 = User.objects.get(id=guest.id)
    if u1.category==u2.category:
        pr=False
    else:
        if u1.category=='Host' and u2.category=='Guest':
            pr=True
        elif u1.category=='Guest' and u2.category=='Host':
            pr=True
        elif u1.category == 'Owner' and u2.category=='Guest' or u2.category=='Host':
            pr = False
        elif u1.category == 'Guest' and u2.category=='Owner':
            pr = False
        elif u1.category == 'Host' and u2.category=='Owner':
            pr = False
        else:
            pr=False
    return pr

def match_exists(room,host,guest):
    return Match.objects.filter(host=host,guest=guest,property=room).exists()
def get_match(room,host,guest):
    return Match.objects.filter(host=host,guest=guest,property=room).first()
def pair_exists(host,guest):
    if Room.objects.filter(host=host).exists():
        pairCheck = PairRequest.objects.filter(host=host,guest=guest)
        # pairCheck = PairRequest.objects.filter(host=host,guest=guest,property=room)
        if pairCheck.exists():
            status=True
        else:
            status=False
    elif Room.objects.filter(host=guest).exists():
        pairCheck = PairRequest.objects.filter(host=guest,guest=host)
        # pairCheck = PairRequest.objects.filter(host=host,guest=guest,property=room)
        if pairCheck.exists():
            status=True
        else:
            status=False
    else:
        status = False
    return status

def get_pair(host,guest):
    if Room.objects.filter(host=host).exists():
        pairCheck = PairRequest.objects.filter(host=host,guest=guest)
        if pairCheck.exists():
            obj=pairCheck.first()
        else:
            obj=None
    elif Room.objects.filter(host=guest).exists():
        pairCheck = PairRequest.objects.filter(host=guest,guest=host)
        if pairCheck.exists():
            obj=pairCheck.first()
        else:
            obj=None
    else:
        obj = None
    return obj

def delete_pair(id):
    pairCheck = PairRequest.objects.filter(id=id)
    if pairCheck.exists():
        PairRequest.objects.get(id=id).delete()
        status=True
    else:
        status=False
    print('deleted')
    return status

def create_pair(host,guest,room,trigger):
    response = False
    if pairable(host,guest) and pair_exists(host,guest):
        id=get_pair(host,guest).id
        print(id,pair_exists(host,guest))
        response = delete_pair(id)
    elif pairable(host,guest) and not pair_exists(host,guest) and not match_exists(room,host,guest):
        new_pair = PairRequest.objects.create(
            rqstId=createId(PairRequest,PairRequest.rqstId,'PRQ'),
            host=host,
            guest=guest,
            property=room,
            trigger=trigger,
            status='Pending',
            seen=False
        )
        if new_pair:
            host.pairs.add(new_pair)
            guest.pairs.add(new_pair)
            response = True
        print('created')
    return response

def suggestRooms(guest_id):
    valid_rooms = []
    valid = 0
    user_obj = User.objects.get(id=guest_id)
    guest_obj = Guest.objects.get(userId=user_obj)
    guest_budget = guest_obj.budget
    guest_loc = guest_obj.userId.location
    guest_age = guest_obj.userId.age
    guest_gender = guest_obj.userId.gender
    guest_hobbies = guest_obj.userId.hobbies.all()
    
    all_rooms = Room.objects.filter(
        Q(location__icontains=guest_loc),
        valid=True,
        available = True
    )
    for room in all_rooms:
        valid = 0
        room_host = User.objects.filter(id=room.host.id)
        if room_host.exists():
            host_id=room.host.id
            room_bookList = room.requestsList
            room_host = User.objects.get(id=host_id)
            room_rent = room.rent
            room_pGender = room.preferredGender
            room_available = room.available
            room_location = room.location
            host_hobbies = room_host.hobbies.all()
            
            if room_available == True and room_host.valid == True and not pair_exists(room_host,user_obj) and not match_exists(room,room_host,user_obj):
                if guest_gender == room_pGender or room_pGender=='Not Necessary':
                    if room_rent <= guest_budget:
                        if not room.requestsList.contains(guest_obj):
                            valid=1
            if valid == 1:
                mutual_hobbies = []
                for hobby in host_hobbies:
                    for gh in guest_hobbies:
                        if hobby == gh:
                            mutual_hobbies.append(hobby)
                # if mutual_hobbies.count()<1:
                #     valid=0
            if valid == 1:
                valid_rooms.append(room)
    return valid_rooms

def suggestHosts(guest_id):
    valid_hosts = []
    valid = 0
    user_obj = User.objects.get(id=guest_id)
    guest_obj = Guest.objects.get(userId=user_obj)
    guest_budget = guest_obj.budget
    guest_loc = guest_obj.userId.location
    guest_age = guest_obj.userId.age
    guest_gender = guest_obj.userId.gender
    guest_hobbies = guest_obj.userId.hobbies.all()
    
    all_hosts = User.objects.filter(
        Q(location__icontains=guest_loc),
        Q(category__icontains='Host')
    )
    for host in all_hosts:
        valid = 0
        host_room = Room.objects.filter(host=host)
        if host_room.exists():
            host_room = Room.objects.get(host=host)
            room_rent = host_room.rent
            room_pGender = host_room.preferredGender
            room_available = host_room.available
            room_location = host_room.location
            host_hobbies = host.hobbies.all()
            
            if room_available == True and room_location.lower()==guest_loc.lower() and not pair_exists(host,user_obj) and not match_exists(host_room,host,user_obj):
                if guest_gender == room_pGender or room_pGender=='Not Necessary':
                    if room_rent <= guest_budget:
                        valid=1
            if valid == 1:
                mutual_hobbies = []
                for hobby in host_hobbies:
                    for gh in guest_hobbies:
                        if hobby == gh:
                            mutual_hobbies.append(hobby)
                # if mutual_hobbies.count()<1:
                #     valid=0
            if valid == 1:
                valid_hosts.append(host)
    return valid_hosts

def suggestGuests(user_id):
    valid_guests = []
    valid = 0
    user_obj = User.objects.get(id=user_id)
    user_rooms = Room.objects.filter(host=user_obj,available=True,valid=True)
    user_location = user_obj.location
    user_gender = user_obj.gender
    user_age = user_obj.age
    user_hobbies = user_obj.hobbies.all()
    
    if user_rooms.exists():
        room_loc = user_rooms.first().location
        all_guests = User.objects.filter(
            Q(location__icontains=room_loc)|
            Q(location__icontains=user_location),
            Q(category__icontains='Guest'),
            valid=True,
            target_met=False
            )
        if all_guests.exists():
            for guest in all_guests:
                valid = 0
                guest_obj = Guest.objects.get(userId=guest)
                guest_location = guest.location
                guest_gender = guest.gender
                guest_age = guest.age
                guest_hobbies = guest.hobbies.all()
                guest_budget = guest_obj.budget
                
                for room in user_rooms:
                    if room.preferredGender == guest_gender or room.preferredGender=='Not Necessary' and not pair_exists(user_obj,guest) and not match_exists(room,user_obj,guest):
                        if room.rent <= guest_budget:
                            valid=1
                            break
                if valid==1:
                    mutual_hobbies = []
                    for hobby in user_hobbies:
                        for gh in guest_hobbies:
                            if hobby == gh:
                                mutual_hobbies.append(hobby)
                    # if mutual_hobbies.count()<1:
                    #     valid=0
                if valid == 1:
                    valid_guests.append(guest)
    
    return valid_guests
                

def suggestPair(user_id):
    pairs = None
    user_obj = User.objects.get(id=user_id)
    acc_type = user_obj.category
    if (acc_type).lower() == 'host':
        acc = 1
    elif (acc_type).lower() == 'guest':
        acc = 2    
    elif (acc_type).lower() == 'owner':
        acc = 3
    else:
        acc = 2
        
    if acc == 1 or acc == 3:
        pairs = suggestGuests(user_id)
    elif acc == 2:
        pairs = suggestRooms(user_id)
    return pairs
    
def createLog(trigger,targetId,act_type,default_text):    
    Log.objects.create(
        actId = createId(Log,Log.actId,'ACT'),
        trigger = trigger,
        target_id = targetId,
        activity_type = act_type,
        default_text = default_text
    )

def delete_match(id):
    res = False
    if Match.objects.filter(id=id).exists():
        match = Match.objects.get(id=id)
        match.delete()
        res = True
    return res

def createMatch(guest,host,room,trigger):
    create_match = False
    created = False
    if User.objects.filter(id=guest.id).exists():
        if User.objects.filter(id=host.id).exists():
            if Room.objects.filter(host=host,id=room.id).exists():
                if not match_exists(room,host,guest):
                    create_match = True
    if match_exists(room,host,guest):
        match=get_match(room,host,guest)
        delete_match(match.id)
    if create_match:
        host_obj = User.objects.get(id=host.id)
        guest_obj = User.objects.get(id=guest.id)
        room_obj = Room.objects.get(id=room.id)
        new_match = Match.objects.create(
            matchId = createId(Match,Match.matchId,'MCH'),
            host = host_obj,
            guest = guest_obj,
            property = room_obj,
            matchType = 'completed'
        )
        if new_match:
            host.matches.add(new_match)
            guest.matches.add(new_match)
            if pair_exists(host,guest):
                pair = get_pair(host,guest)
                delete_pair(pair.id)
            if same_user(trigger,host):
                target = guest
            elif same_user(trigger,guest):
                target = host
            else:
                target = new_match
                
            send_notification(
                'It\'s a match! You have successfully matched with '+str(trigger.get_full_name())+'. Take things to the next level and start preparing your new property.',
                'New Match',
                trigger,
                target,
                'Match',
                "/profiles/"+str(trigger.id)
            )
            created = True
    return created

def book_room(guest,owner,room):
    res = False
    if User.objects.filter(id=guest.id).exists() and User.objects.filter(id=owner.id).exists() and Room.objects.filter(id=room.id).exists():
        user_obj = User.objects.get(id=guest.id)
        owner_obj = User.objects.get(id=owner.id)
        room_obj = Room.objects.get(id=room.id)
        Guest.objects.get_or_create(userId=user_obj)
        guest_obj=Guest.objects.get(userId=user_obj)
        if room_obj.requestsList.contains(guest_obj):
            room_obj.requestsList.remove(guest_obj)
        else:
            room_obj.requestsList.add(guest_obj)
        
        send_notification(
            str(user_obj.get_full_name())+' sent you a request for an apartment/room. Check out their profile to see more.',
            'Room Request',
            user_obj,
            owner_obj,
            'Room Request',
            '/profiles/'+str(user_obj.id)
        )
        createLog(
            user_obj,
            room_obj.id,
            'Property',
            str(user_obj.get_full_name())+' requested for a room.'
        )
        res = True
    return res

def guest_has_requested(guest,room):
    res=False
    if room.requestsList.contains(guest):
        res = True
    return res

def booked_rooms(guest):
    res=[]
    if guest is not None and Guest.objects.filter(id=guest.id).exists():
        guest_obj = Guest.objects.get(id=guest.id)
        booked_rooms = Room.objects.exclude(requestsList=None)
        for room in booked_rooms:
            res.append(room)
    return res