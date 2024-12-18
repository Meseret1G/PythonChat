from django.contrib import admin
from .models import ChatModel,FriendList,FriendRequest,Friendship,PasswordReset

class ChatModelAdmin(admin.ModelAdmin):
    list_display = ('sender', 'message', 'display_file', 'thread_name', 'timestamp')

    def display_file(self, obj):
        if obj.file:
            return f'<a href="{obj.file.url}" target="_blank">{obj.file.name}</a>'
        return 'No file'

    display_file.allow_tags = True
    display_file.short_description = 'File'

admin.site.register(ChatModel, ChatModelAdmin)
admin.site.register(FriendList)
admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(PasswordReset)