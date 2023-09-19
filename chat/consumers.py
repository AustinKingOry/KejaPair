import json
import os
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from chat.models import Thread, Chat,User
from django.conf.global_settings import SECRET_KEY
from base.basicFunctions import createId,encrypt_text

class ChatConsumer(AsyncConsumer):
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
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')
        if thread_id == "create_new":
            thread_id = None

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id,sent_by_id,send_to_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect',send_to_id)
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        status=await self.create_chat_message(thread_obj, sent_by_user, msg)

        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        response = {
            'message': msg,
            'sent_by': self_user.id,
            'thread_id': thread_obj.id,
            'sender_name': self_user.username,
            'sender_img': self_user.profilePhoto.url,
            'status': status
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
        print('chat_message', event)
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
    def get_thread(self, thread_id,p1_id,p2_id):
        if thread_id is not None:
            qs = Thread.objects.filter(id=thread_id)
            if qs.exists():
                obj = qs.first()
            else:
                obj = None
        else:
            p1exists = User.objects.get(id=p1_id)
            p2exists = User.objects.get(id=p2_id)
            if User.objects.filter(id=p1_id).exists() and User.objects.filter(id=p2_id).exists():
                obj = Thread.objects.create(
                    first_person = p1exists,
                    second_person = p2exists,
                )
            else:
                obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        status = False
        secret_key=b'*#*#@kejapair#*#'
        # secret_key = SECRET_KEY
        msg = encrypt_text(secret_key,msg)
        chat_save = Chat.objects.create(
            thread=thread,
            user=user,
            body=msg,
            msgId = createId(Chat,Chat.msgId,'MSG'),
        )
        if chat_save:
            status=True
        return status
        
        
        
class ChatSeenConsumer(AsyncConsumer):
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
        msg = received_data.get('')
        sent_by_id = received_data.get('chat_sender')
        send_to_id = received_data.get('chat_receiver')
        thread_id = received_data.get('chat_thread')
        
        if  not thread_id:
            print('Error:: empty thread')
            return False

        if not send_to_id:
            print('Error:: empty receiver')
            return False
        
        if not sent_by_id:
            print('Error:: empty sender')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect',send_to_id)
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        status = await self.mark_chat_as_read(thread_obj, sent_by_user)

        other_user_chat_room = f'user_chatroom_{sent_by_id}'
        self_user = self.scope['user']
        response = {
            'feedback': msg,
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
        print('chat_message', event)
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
    def get_thread(self, thread_id):
        if thread_id is not None:
            qs = Thread.objects.filter(id=thread_id)
            if qs.exists():
                obj = qs.first()
            else:
                obj = None
        else:
            obj = None
        return obj

    @database_sync_to_async
    def mark_chat_as_read(self, thread_obj, user_obj):
        sbj_chat = Chat.objects.filter(thread=thread_obj,user=user_obj)
        if sbj_chat:
            for chat in sbj_chat:
                chat.unread=False
                chat.receiverNotified=True
                chat.save()
            return True
        else:
            return False        