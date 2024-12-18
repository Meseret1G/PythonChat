from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from django.utils import timezone
class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    file= models.FileField(upload_to='chat_files/',null=True,blank=True)

    def __str__(self) -> str:
        return self.message if self.message else "No message"
    class Meta:
        ordering = ['timestamp'] 

class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_list')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        if account not in self.friends.all():
            self.friends.add(account) 

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account) 

    def unfriend(self, removee):
        self.remove_friend(removee)
        
        try:
            friends_list = FriendList.objects.get(user=removee)
            friends_list.remove_friend(self.user)
        except FriendList.DoesNotExist:
            raise ValueError("Friend list does not exist for the user being removed.")

    def is_mutual_friend(self, friend):
        return friend in self.friends.all()
    
class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(blank=False, null=False, default=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        sender_friend_list = FriendList.objects.get(user=self.sender)

        if receiver_friend_list and sender_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list.add_friend(self.receiver)
            self.is_active = False
            self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()

class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friends1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friends2", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('removed', 'Removed')])

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} - {self.user2.username} ({self.status})"

    def remove_friendship(self):
        self.status = 'removed'
        self.save()
    def accept_friendship(self):
        self.status = 'accepted'
        self.save()

    def cancel_friendship(self):
        self.status = 'pending'
        self.save()


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification for {self.user.username}"