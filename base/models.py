from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.contrib.auth.models import User

class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    file= models.FileField(upload_to='chat_files/',null=True,blank=True)

    def __str__(self) -> str:
        return self.message
    class Meta:
        ordering = ['timestamp'] 


# class Group(models.Model):
#     name = models.CharField(max_length=255, unique=True)
#     members = models.ManyToManyField(User, related_name="groups")

#     def __str__(self):
#         return self.name


# class Message(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ('timestamp',)

#     def __str__(self):
#         return f"{self.user.username}: {self.content}"



# import uuid

# class PasswordReset(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
#     created_when = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Password reset for {self.user.username} at {self.created_when}"
