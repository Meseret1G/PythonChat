import datetime
import json
import uuid
import os
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
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
        await self.send_chat_history()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        print(f"Received Data: {data}") 

        message = data.get('message', '') 
        username = data['username']
        file_data = data.get('file', None)

        file_url = None  
        timestamp = datetime.datetime.now().isoformat() 
        if file_data:
            try:
                if ';base64,' not in file_data:
                    raise ValueError("Invalid base64 file format")
                
                format, imgstr = file_data.split(';base64,') 
                ext = format.split('/')[-1]  
                file_content = base64.b64decode(imgstr) 
                os.makedirs('media/uploads', exist_ok=True)

                filename = f"{uuid.uuid4()}.{ext}"
                file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

                with open(file_path, "wb") as f:
                    f.write(file_content)

                file_url = f"/media/uploads/{filename}"  
            except Exception as e:
                print(f"Error processing file: {e}")
                await self.send(text_data=json.dumps({
                    'error': f"Error processing file: {str(e)}"
                }))
                return  

        await self.save_message(username, self.room_name, message, file_url)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "username": username,
                "file": file_url,
                "timestamp": timestamp,  
            },
        )


    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        file_url = event['file']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'file': file_url,
            'timestamp': timestamp
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

    @database_sync_to_async
    def get_chat_history(self, room_name):
        messages = ChatModel.objects.filter(thread_name=room_name).order_by('timestamp')
        chat_history = []
        for message in messages:
            chat_history.append({
                'message': message.message,
                'username': message.sender,
                'file': message.file.url if message.file else None,
                'timestamp': message.timestamp.isoformat(),
            })
        return chat_history

    async def send_chat_history(self):
        chat_history = await self.get_chat_history(self.room_name)
        for message in chat_history:
            await self.send(text_data=json.dumps(message))
