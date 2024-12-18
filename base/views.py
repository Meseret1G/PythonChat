from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from base.models import *
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect,get_list_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from base.forms import *
from django.contrib.auth import update_session_auth_hash


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

    friendship = Friendship.objects.filter(
        (Q(user1=request.user) & Q(user2=user_obj)) | (Q(user1=user_obj) & Q(user2=request.user))
    ).first()

    if friendship:
        print(f"Friendship status: {friendship.status}")
    else:
        print("No friendship found.")

    if friendship and friendship.status == 'accepted':
        if request.user.id > user_obj.id:
            thread_name = f'chat_{request.user.id}-{user_obj.id}'
        else:
            thread_name = f'chat_{user_obj.id}-{request.user.id}'

        message_obj = ChatModel.objects.filter(thread_name=thread_name).order_by('timestamp')
        return render(request, 'chat_area.html', context={'users': users, 'user': user_obj, 'messages': message_obj})

    messages.error(request, "You cannot chat with this user.")
    return redirect('home')


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    if query:
        users = User.objects.filter(username__icontains=query)[:10] 
        users_data = [{"username": user.username} for user in users]
        return JsonResponse(users_data, safe=False)
    return JsonResponse([], safe=False)

def get_all_users(request):
    logged_in_user = request.user
    users = User.objects.exclude(id=logged_in_user.id)[:10]  
    users_data = [{"username": user.username} for user in users]
    
    return JsonResponse(users_data, safe=False)

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

@login_required
def LogoutView(request):

    logout(request)

    return redirect('login')

@login_required
def edit_user_info(request):
    print(f":User  {request.user}")  
    if request.method == 'POST':
        form = UserInfoEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, "YOUR INFORMATION WAS UPDATED SUCCESSFULLY")
            if 'password' in form.changed_data:
                update_session_auth_hash(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'There was an error updating your information')
            print(form.errors)
    else:
        form = UserInfoEditForm(instance=request.user)
    return render(request, 'edit_user_info.html', {'form': form})

@login_required
def profile_view(request):
    friend_list, created = FriendList.objects.get_or_create(user=request.user)
    incoming_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True) 
    outgoing_requests = FriendRequest.objects.filter(sender=request.user, is_active=True)
    
    context = {
        'friend_list': friend_list,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    }
    return render(request, 'profile.html', context)


@login_required
def get_user_info(request, username):
    user = get_object_or_404(User, username=username)
    return JsonResponse({
        'username': user.username,
        'email': user.email,
    })

@login_required
def send_friend_request(request, username):
    if request.method == "POST":
        receiver = get_object_or_404(User, username=username)
        requester = request.user

        if requester == receiver:
            return JsonResponse({'success': False, 'message': 'You cannot send a friend request to yourself.'})

        if FriendRequest.objects.filter(sender=requester, receiver=receiver, is_active=True).exists():
            return JsonResponse({'success': False, 'message': 'Friend request already sent.'})

        FriendRequest.objects.create(sender=requester, receiver=receiver)

        return JsonResponse({'success': True, 'message': 'Friend request sent.'})
    
@login_required
def accept_friend_request(request, request_id):
    if request.method == "POST":
        friend_request = get_object_or_404(FriendRequest, id=request_id, is_active=True)

        friendship, created = Friendship.objects.get_or_create(
            user1=friend_request.sender,
            user2=friend_request.receiver,
            defaults={'status': 'accepted'}
        )

        if created:
            friend_request.accept()  
            return JsonResponse({'success': True, 'message': 'Friend request accepted.'})
        else:
            return JsonResponse({'success': False, 'message': 'Friendship already exists.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
def ForgotPassword(request):

    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email] 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')

def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                return redirect('reset-password', reset_id=reset_id)

    
    except PasswordReset.DoesNotExist:
        
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')
@login_required
def decline_friend_request(request,request_id):
    friend_request=FriendRequest.objects.get(id=request_id)
    if friend_request.reciever!=request.user:
        raise Http404("This request is not fro you")
    
    friend_request.decline()
    return redirect('profile',username=request.user.username)

def are_friends(request, username):
    try:
        target_user = get_object_or_404(User, username=username)
        user = request.user

        friendship = Friendship.objects.filter(
            (Q(user1=user) & Q(user2=target_user) & Q(status='accepted')) |
            (Q(user1=target_user) & Q(user2=user) & Q(status='accepted'))
        ).exists()

        return JsonResponse({'are_friends': friendship})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
from django.shortcuts import get_object_or_404, redirect
from .models import User, Friendship

def remove_friend(request, username):
    user_to_remove = get_object_or_404(User, username=username)
    friendship = Friendship.objects.filter(
        (Q(user1=request.user) & Q(user2=user_to_remove)) |
        (Q(user1=user_to_remove) & Q(user2=request.user))
    ).first()

    if friendship:
        friendship.delete()  
        messages.success(request, f"You have removed {user_to_remove.username} from your friends.")
    else:
        messages.error(request, "This user is not your friend.")
    
    return redirect('home')  
