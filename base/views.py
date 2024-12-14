from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from base.models import ChatModel
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect,get_list_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

@login_required
def index(request):
    users=User.objects.exclude(username=request.user.username)
    return render(request,'index.html',context={'users':users})

@login_required
def chatPage(request, username):
    try:
        user_obj = get_object_or_404(User, username=username)
    except User.DoesNotExist:
        raise Http404("The user does not exist.")

    users = User.objects.exclude(username=request.user.username)

    if request.user.id> user_obj.id:
        thread_name =f'chat_{request.user.id}-{user_obj.id}'
    else:
        thread_name =f'chat_{user_obj.id}-{request.user.id}'
    
    message_obj = ChatModel.objects.filter(thread_name=thread_name).order_by('timestamp')
    return render(request, 'chat_area.html', context={'users': users, 'user': user_obj,'messages':message_obj})

def RegisterView(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_data_has_error =False
        
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

        if len(password)<8:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 8 characters')
        
        if not user_data_has_error:
            new_user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password
            )
            messages.success(request, 'Account created. Login now')
            return redirect('login')
        else:
            return redirect('register')
        
    return render (request,'register.html')

def LoginView(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            next_url = request.GET.get('next', '/default-redirect-url/')  
            return redirect(next_url)
    return render(request,'login.html')

def LogoutView(request):

    logout(request)

    return redirect('login')