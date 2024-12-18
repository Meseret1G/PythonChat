from django import forms
from django.contrib.auth.models import User

class UserInfoEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']  

class UserSearchForm(forms.Form):
    query = forms.CharField(label='Search Users', max_length=100)