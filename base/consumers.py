import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from chat.models import Chat,Thread
from base.models import Property,Like,Hobby,User,RoomPhoto,Notification,ActivityLog as Log
from base.utils import createId,send_notification,suggestPair,createLog
from django.db.models import Q


class RoomLikesConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        room_id = received_data.get('room_id')
        liked_by = received_data.get('liked_by')
       
        if not room_id:
            print('Error:: empty room')
            return False
        
        if not liked_by:
            print('Error:: empty user')
            return False

        room = await self.get_room_object(room_id)
        room_owner = await self.get_host_object(room_id)
        liked_by_user = await self.get_user_object(liked_by)
        if not room:
            print('Error:: room is incorrect')
        if not liked_by_user:
            print('Error:: user is incorrect')

        status = await self.submit_reaction(room, liked_by_user,room_owner)
        # if status == True:
        #     feedback = 'Success!'
        # else:
        #     feedback = 'Failed!'
        room_likes = await self.get_room_likes(room_id)

        other_user_chat_room = f'user_chatroom_{room_owner}'
        self_user = self.scope['user']
        response = {
            'feedback': 'Success!',
            'total_likes':room_likes,
            'reaction_type': status,
        }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    @database_sync_to_async
    def get_host_object(self,room_id):
        qs = Property.objects.filter(id=room_id)
        if qs.exists():
            room_obj = qs.first()
            obj = room_obj.host
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_room_object(self, room_id):
        if room_id is not None:
            qs = Property.objects.filter(id=room_id)
            if qs.exists():
                obj = qs.first()
            else:
                obj = None
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_room_likes(self, room_id):
        if room_id is not None:
            qs = Property.objects.filter(id=room_id)
            if qs.exists():
                obj = qs.first()
                likes = obj.likesCount
            else:
                obj = None
                likes = 0
        else:
            obj = None
            likes = 0
        return likes
    
    @database_sync_to_async
    def submit_reaction(self, room_obj, liked_by_obj,owner_obj):
        existing_reaction = Like.objects.filter(host=owner_obj,guest=liked_by_obj,property=room_obj)
        if existing_reaction.exists():
            action = 0
            for reaction in existing_reaction:
                reaction.delete()
            
            sbj_room = Property.objects.filter(id=room_obj.id)
            if sbj_room:
                for room in sbj_room:
                    if room.likesCount < 0:
                        room.likesCount = 0
                    else:
                        room.likesCount-=1
                    room.save()
                status = True
            else:
                status = False
            return action
        else:
            action = 1
            Like.objects.create(
                likeId = createId(Like,Like.likeId,'LK'),
                host  = owner_obj,
                guest = liked_by_obj,
                property = room_obj,
            )
            
            sbj_room = Property.objects.filter(id=room_obj.id)
            if sbj_room:
                for room in sbj_room:
                    if room.likesCount < 0:
                        room.likesCount = 0
                    else:
                        room.likesCount+=1                    
                    room.save()
                status = True
                createLog(
                    trigger = liked_by_obj,
                    targetId = room_obj.id,
                    act_type = 'Like',
                    default_text = str(liked_by_obj.username) + ' liked the room:' + str(room_obj.name)
                )
            else:
                status = False
            if status == True:
                if liked_by_obj != owner_obj:
                    send_notification(
                        str(liked_by_obj.first_name)+' '+str(liked_by_obj.last_name)+' likes your room. Get in touch with them to see if you match interests.',
                        'New Reaction From Listing',
                        liked_by_obj,
                        owner_obj,
                        'Like',
                        "/profiles/"+str(liked_by_obj.id)
                    )
            return action
        
        
        
class NewHobbiesConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        hobby_list = received_data.get('hobby_list')
        request_user_id = received_data.get('request_user')
       
        if not request_user_id:
            print('Error:: empty user')
            return False
        
        if not hobby_list:
            print('Error:: empty hobbies')
            return False

        hobbies_user = await self.get_user_object(request_user_id)
        if not hobbies_user:
            print('Error:: user is incorrect')
        hobbies = await self.get_user_hobbies(request_user_id)

        status = await self.submit_hobbies(hobbies_user,hobby_list)

        other_user_chat_room = f'user_chatroom_{hobbies_user}'
        self_user = self.scope['user']
        response = {
            'feedback': 'hobbies updated successfully!',
            'hobbies':hobbies,
            'status': status,
        }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_user_hobbies(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            user = User.objects.get(id=user_id)
            hobbies = user.hobbies.all()
            obj=[]
            for hobby in hobbies:
                obj.append(hobby.name)
            print(obj)
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def submit_hobbies(self, user_obj, hobbies_list):
        counter = 1
        for hobby in hobbies_list:
            existing_hobby = Hobby.objects.filter(name=hobby)
            if existing_hobby.exists():
                existing_hobby_obj=Hobby.objects.get(name=hobby)
                existing_hobby_id = existing_hobby_obj.id
                print('\n'+str(existing_hobby_id)+'\n\n')
                action = 0
                # for reaction in existing_reaction:
                #     reaction.delete()
                
                sbj_user = User.objects.get(id=user_obj.id)
                if sbj_user:
                    if counter == 1:
                        allhobbies=sbj_user.hobbies.all()
                        sbj_user.hobbies.clear()
                        # for h in allhobbies:
                        #     h.delete()
                    # user_hobbies = sbj_user.hobbies.filter(id=existing_hobby_id)
                    # if not user_hobbies.exists():
                    sbj_user.hobbies.add(existing_hobby_id)
                    sbj_user.save()
                    status = True
                    # else:
                    #     status=False
                else:
                    status = False
            else:
                action = 1
                hobby_field=Hobby.objects.create(                
                    hbId = createId(Hobby,Hobby.hbId,'HBY'),
                    name = hobby,
                )            
                sbj_user = User.objects.get(id=user_obj.id)
                if sbj_user:
                    if counter == 1:
                        allhobbies=sbj_user.hobbies.all()
                        sbj_user.hobbies.clear()
                        # for h in allhobbies:
                        #     h.delete()
                    sbj_user.hobbies.add(hobby_field)
                    sbj_user.save()
                    status = True
                else:
                    status = False
            counter+=1
        if status == True:            
            createLog(
                trigger = user_obj,
                targetId = user_obj.id,
                act_type = 'Hobby',
                default_text = str(user_obj.username) + ' updated their hobbies.'
            )
        return status
    
        
class HandlePhotosConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        photo_id = received_data.get('photo_id')
        rqst_type = received_data.get('rqst_type')
        img_table = received_data.get('desk')        
        request_user_id = received_data.get('request_user')
        request_room_id = received_data.get('request_room')
       
        if not request_user_id:
            print('Error:: empty user')
            return False
        
        if not photo_id:
            print('Error:: empty photo')
            return False
        
        if not rqst_type:
            print('Error:: empty request type')
            return False
        
        if not img_table:
            print('Error:: empty desk')
            return False

        photo_user = await self.get_user_object(request_user_id)
        if not photo_user:
            print('Error:: user is incorrect')
        photo_in_record = await self.get_photo(request_user_id,photo_id,img_table)
        if not photo_in_record:
            print('Error:: photo is incorrect')
        room_obj = await self.get_room_object(request_room_id,photo_user)
        if not room_obj:
            print('Error:: room is incorrect')

        if str(rqst_type).lower() == 'del':
            status = await self.del_photo(photo_user,photo_in_record,img_table)
        elif str(rqst_type).lower() == 'cover':
            status = await self.set_cover_photo(room_obj,photo_user,photo_in_record)
        else:
            status = 'Invalid request!'

        other_user_chat_room = f'user_chatroom_{photo_user}'
        self_user = self.scope['user']
        response = {
            'feedback': status,
            'status': status,
        }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_room_object(self,room_id,user_obj):
        room = Property.objects.filter(id=room_id,host=user_obj)
        if room.exists():
            obj = Property.objects.get(id=room_id)
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_photo(self, user_id,photo_id,table_name):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            user = User.objects.get(id=user_id)
            
            if str(table_name).lower() == 'house':
                sbj_table = Property
                sbj_room = Property.objects.filter(id=photo_id)
                if sbj_room.exists():
                    obj = Property.objects.get(id=sbj_room.first().id)
                else:
                    obj=None
            elif str(table_name).lower() == 'house_photo':
                sbj_table = RoomPhoto
            
                sbj_photo = RoomPhoto.objects.filter(id=photo_id)
                if sbj_photo.exists():
                    obj = RoomPhoto.objects.get(id=sbj_photo.first().id)
                else:
                    obj=None
                    
            else:
                obj = None
        else:
            obj = None
        return obj

    @database_sync_to_async
    def del_photo(self,user_obj,photo_obj,img_table):
        if str(img_table).lower() == 'house_photo':            
            photo = RoomPhoto.objects.filter(id=photo_obj.id,host=user_obj)
            if photo.exists():
                photo = RoomPhoto.objects.get(id=photo_obj.id)
                photo.delete()
                response = "Photo deleted successfully!"
            else:
                response = 'Photo does not exist!'
        elif str(img_table).lower() == 'cover':
            photo = Property.objects.filter(id=photo_obj.id,host=user_obj)
            response = 'You cannot delete the room\'s cover photo'
        else:
            response = 'Error in identifying the photo. Try again.'
        return response
            

    @database_sync_to_async
    def set_cover_photo(self,room_obj,user_obj,photo_obj):
        photo = RoomPhoto.objects.filter(id=photo_obj.id)
        if photo.exists():
            photo = RoomPhoto.objects.get(id=photo_obj.id)
            photo_url = photo.image
            sbj_room = Property.objects.filter(id=room_obj.id,host=user_obj)
            if sbj_room.exists():
                sbj_room = Property.objects.get(id=room_obj.id)
                cur_cover = sbj_room.coverPhoto
                new_photo = RoomPhoto.objects.create(
                    photoId = createId(RoomPhoto,RoomPhoto.photoId,'PHR'),
                    host = user_obj,
                    room = room_obj,
                    image = cur_cover,
                    category = 'room',
                    description = '',
                )
                sbj_room.photosList.add(new_photo)
                sbj_room.coverPhoto = photo_url
                sbj_room.save()
                photo.delete()
                response = 'Cover photo updated successfully.'
                createLog(
                    trigger = user_obj,
                    targetId = room_obj.id,
                    act_type = 'RoomPhoto',
                    default_text = str(user_obj.username) + ' updated the cover photo for their room.'
                )
            else:
                response = 'No such room.'
        else:
            response = 'Photo does not exist'
        return response


class ClearNotificationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        notif_id = received_data.get('notif_id')
        rqst_type = received_data.get('rqst_type')    
        request_user_id = received_data.get('request_user')
       
        if not request_user_id:
            print('Error:: empty user')
            return False
        
        if not notif_id:
            print('Error:: empty notification')
            return False
        
        if not rqst_type:
            print('Error:: empty request type')
            return False
        
        notif_user = await self.get_user_object(request_user_id)
        if not notif_user:
            print('Error:: user is incorrect')
        notif_obj = await self.get_notification(notif_user,notif_id)
        if not notif_obj:
            print('Error:: notification is incorrect')

        if str(rqst_type).lower() == 'clear':
            status = await self.clear(notif_user,notif_obj,notif_id)
        else:
            status = False

        other_user_chat_room = f'user_chatroom_{notif_user}'
        self_user = self.scope['user']
        if(status==True):
            feedback='Cleared'
        else:
            feedback='Failed.'
        response = {
            'feedback': feedback,
            'status': status,
        }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_notification(self, user_obj,notif_id):
        qs = User.objects.filter(id=user_obj.id)
        if qs.exists():
            user = User.objects.get(id=user_obj.id)
            if notif_id != '*':
                sbj_notification = Notification.objects.filter(id=notif_id,user=user_obj)
                if sbj_notification.exists():
                    obj = Notification.objects.get(id=sbj_notification.first().id)
                else:
                    obj=None
            else:
                sbj_notification = Notification.objects.filter(user=user_obj)
                if sbj_notification.exists():
                    obj = Notification.objects.get(id=sbj_notification.first().id)
                else:
                    obj=None
        else:
            obj = None
        return obj

    @database_sync_to_async
    def clear(self,user_obj,notif_obj,notif_id):
        if notif_id == '*':
            notification = Notification.objects.filter(user=user_obj,seen=False)
            if notification.exists():
                for obj in notification:
                    notification = Notification.objects.get(id=obj.id)
                    notification.seen=True
                    notification.save()
                response = True
            else:
                response = False
        else:
            notification = Notification.objects.filter(id=notif_obj.id,user=user_obj)
            if notification.exists():
                notification = Notification.objects.get(id=notif_obj.id)
                notification.seen=True
                notification.save()
                response = True
            else:
                response = False
        return response


class LiveDataConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        rqst_type = received_data.get('rqst_type')    
        request_user_id = received_data.get('request_user')
       
        if not request_user_id:
            print('Error:: empty user')
            return False
        
        if not rqst_type:
            print('Error:: empty request type')
            return False
        
        request_user = await self.get_user_object(request_user_id)
        if not request_user:
            print('Error:: user is incorrect')
        notif_count = await self.get_notifications_count(request_user)
        pairs_count = await self.get_pairs_count(request_user)
        chats_count = await self.get_chats_count(request_user)
        total_count = int(notif_count)+int(pairs_count)+int(chats_count)


        other_user_chat_room = f'live_data_{request_user}'
        self_user = self.scope['user']
        response = {
            'total_count': total_count,
            'notif_count': notif_count,
            'pairs_count': pairs_count,
            'chats_count': chats_count,
            'status': True,
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_notifications_count(self, user_obj):
        qs = User.objects.filter(id=user_obj.id)
        if qs.exists():
            user = User.objects.get(id=user_obj.id)
            sbj_notification = Notification.objects.filter(user=user,seen=False)
            
            if sbj_notification.exists():
                obj = sbj_notification.count()
            else:
                obj=0
        else:
            obj = 0
        return obj
    
    
    @database_sync_to_async
    def get_chats_count(self, user_obj):
        qs = User.objects.filter(id=user_obj.id)
        if qs.exists():
            user = User.objects.get(id=user_obj.id)
            all_threads = Thread.objects.filter(
                Q(first_person=user) |
                Q(second_person=user) 
            )
            chat_counter = 0
            for thread in all_threads:
                if thread.first_person == user:
                    sender = thread.second_person
                    sbj_chat = Chat.objects.filter(thread=thread,receiverNotified=False,unread=True,user=sender)            
                    if sbj_chat.exists():
                        chat_counter += sbj_chat.count()
                    else:
                        chat_counter+=0
                        
                elif thread.second_person == user:
                    sender = thread.first_person
                    sbj_chat = Chat.objects.filter(thread=thread,receiverNotified=False,unread=True,user=sender)            
                    if sbj_chat.exists():
                        chat_counter += sbj_chat.count()
                    else:
                        chat_counter+=0
                else:
                    chat_counter+=0
        else:
            chat_counter = 0
        return chat_counter

    @database_sync_to_async
    def get_pairs_count(self, user_obj):
        qs = User.objects.filter(id=user_obj.id)
        if qs.exists():
            user = User.objects.get(id=user_obj.id)
            user_pairs = user.pairs.filter(seen=False)
            
            if user_pairs.exists():
                obj = user_pairs.count()
            else:
                obj=0
        else:
            obj = 0
        return obj
    
    
class ReccomendPairConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        rqst_type = received_data.get('rqst_type')    
        request_user_id = received_data.get('request_user')
       
        if not request_user_id:
            print('Error:: empty user')
            return False
        
        if not rqst_type:
            print('Error:: empty request type')
            return False
        
        request_user = await self.get_user_object(request_user_id)
        if not request_user:
            print('Error:: user is incorrect')
        suggested_pairs = await suggestPair(request_user)


        other_user_chat_room = f'live_data_{request_user}'
        self_user = self.scope['user']
        response = {
            'pairs_count': suggested_pairs,
            'status': True,
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    