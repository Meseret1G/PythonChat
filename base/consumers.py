import datetime
import json
from django.core.files.base import ContentFile
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from base.models import ChatModel
class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        other_id = self.scope['url_route']['kwargs']['id']
        
        if int(my_id) > int(other_id):
            self.room_name = f'{my_id}-{other_id}'
        else:
            self.room_name = f'{other_id}-{my_id}'
        
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        file_data = data.get('file', None)

        file_url = None  

        if file_data:
            format, imgstr = file_data.split(';base64,')  
            ext = format.split('/')[-1] 
            file = ContentFile(base64.b64decode(imgstr), name=f"file.{ext}") 
            file_url = await self.save_message(username, self.room_group_name, message, file)
        else:
            file_url = await self.save_message(username, self.room_group_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'file': file_url,  
                'timestamp': datetime.datetime.now().isoformat()
            }
        )
    
    async def chat_message(self,event):
        message = event['message']
        username=event['username']
        
        await self.send(text_data = json.dumps({
            'message':message,
            'username':username,
            'file': event['file'],
            'timestamp': event['timestamp']
        }))
    @database_sync_to_async
    def save_message(self, username, thread_name, message, file=None):
        chat_message = ChatModel.objects.create(
            sender=username,
            message=message,
            thread_name=thread_name,
            file=file
        )
        return chat_message.file.url if chat_message.file else None 

# class OnlineStatusConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name ='user'
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )       
        
#         await self.accept()
        
#     async def disconnect(self,message):
#         self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
        