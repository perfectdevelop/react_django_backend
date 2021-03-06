from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
import math
import requests
import time
import datetime
import json
import os 
import random
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm

from account.models import CustomUser,Follows,Experience,Education,Visiter,Notification
from blog.models import Posts,Likes,Comments,PostAttach,LikesComment,Replies,LikesReply
from chat.models import Room,Message
import datetime
from datetime import timedelta
import random
import string
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate, logout
from PIL import Image
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
# from twilio.rest import Client
# from sinchsms import SinchSMS 
# from textmagic.rest import TextmagicRestClient
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'


class RegisterView(generic.CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


def check_auth(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    else:
        return True

PAGINATION_COUNT = 21
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_geolocation_for_ip(ip):
    url = f"http://api.ipstack.com/{ip}?access_key=48ff15e0e6d7fde5fbcf780a6adbc287"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
def get_curuser(request,user_id):
    user = request.user
    curuser = {}
    row = CustomUser.objects.get(id=user_id)    
    
    if row.avatar:
        curuser['avatar']=row.avatar.url
    else:
        curuser['avatar']='/static/images/user.png'
    if user_id == user.id:
        curuser['me']='1'
    else:
        curuser['me']='0'
    curuser['aboutme']=row.aboutme
    curuser['username']=row.username
    curuser['firstname']=row.first_name
    curuser['lastname']=row.last_name
    curuser['id']=row.id
    curuser['followers']=Follows.objects.filter(whom=row.id).count()        
    curuser['following']=Follows.objects.filter(who=row.id).count()
    curuser['connections']='0'
    curuser['created_at']=row.created_at
    curuser['gender']=row.gender
    curuser['jobtitle']=row.jobtitle
    curuser['location']=row.location
    curuser['linkInstagram']=row.linkInstagram
    curuser['linkFacebook']=row.linkFacebook
    curuser['linkTwitter']=row.linkTwitter
    curuser['linkYoutube']=row.linkYoutube
    curuser['linkGithub']=row.linkGithub
    curuser['public_email']=row.public_email
    curuser['public_phone']=row.public_phone
    curuser['public_birth']=row.public_birth
    curuser['email']=row.email
    curuser['phone']=row.phone
    curuser['phone_code']=row.phone_code
    curuser['birth']=row.birthDay+"/"+row.birthMonth+"/"+row.birthYear
    if row.back:
        curuser['back'] = row.back.url
    else:
        curuser['back'] = '/static/images/facebook-cover.jpg'
    if Follows.objects.filter(who=user.id,whom=user_id).count():
        curuser['followed']='1'
    else :
        curuser['followed']='0'

    return curuser
def get_users(request):
    user = request.user
    follow_id_array = []
    followtemp = Follows.objects.filter(who=user.id)
    for item in followtemp:
        follow_id_array.append(item.whom)
    follow_id_array.append(user.id)

    userstemp = CustomUser.objects.exclude(id__in=follow_id_array).filter(location=user.location)
    
    users=[]
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = '/static/images/user.png'       
        if Follows.objects.filter(who=user.id,whom=item.id).count() :
            data['followed']='1'
        else :
            data['followed']='0'
        users.append(data)

    return users

def get_users_following(user_id):
    
    follow_id_array = []
    followtemp = Follows.objects.filter(who=user_id)
    for item in followtemp:
        follow_id_array.append(item.whom)
    
    userstemp = CustomUser.objects.filter(id__in=follow_id_array)
    
    followingusers=[]
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = '/static/images/user.png'       
        
        followingusers.append(data)

    return followingusers

def get_following(request):    
    user = request.user
    followingtemp = Follows.objects.filter(who=user.id)
    followingarray = []
    for item in followingtemp:
        followingarray.append(item.whom)        
    userstemp = CustomUser.objects.filter(id__in=followingarray)
    users=[]
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = ''       
        if Follows.objects.filter(who=user.id,whom=item.id).count() :
            data['followed']='1'
        else :
            data['followed']='0'
        users.append(data)

    return users

def get_followers(request):    
    user = request.user
    followingtemp = Follows.objects.filter(whom=user.id)
    followingarray = []
    for item in followingtemp:
        followingarray.append(item.who)        
    userstemp = CustomUser.objects.filter(id__in=followingarray)
    users=[]
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = ''       
        if Follows.objects.filter(who=user.id,whom=item.id).count() :
            data['followed']='1'
        else :
            data['followed']='0'
        users.append(data)

    return users



def get_different_time(orgtime):
    
    curtime = datetime.datetime.now()
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    date1 = orgtime.strftime('%Y-%m-%d %H:%M:%S.%f')
    date2 = curtime.strftime('%Y-%m-%d %H:%M:%S.%f')
    diff = datetime.datetime.strptime(date2, datetimeFormat)\
        - datetime.datetime.strptime(date1, datetimeFormat)    
    
    result = ''
    if(int(diff.days) > 0):
        result = diff.days       
        if(int(result)>30):
            result = math.ceil(int(result)/30)
            result = str(result)+"Months"
        else:
            result = str(result)+"Days"
    else:
        result = diff.seconds
        if(int(result) > 3600):
            result = math.ceil(int(result)/3600)
            result = str(result)+"Hours"
        else:
            result = math.ceil(int(result)/60)+1
            result = str(result)+"Mins"
    return result

def get_date_str(orgtime):
    result = ''
    curtime = datetime.datetime.now()
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    date1 = orgtime.strftime('%Y-%m-%d %H:%M:%S.%f')
    date2 = curtime.strftime('%Y-%m-%d %H:%M:%S.%f')
    diff = datetime.datetime.strptime(date2, datetimeFormat)\
        - datetime.datetime.strptime(date1, datetimeFormat)        
    if(int(diff.days) < 1):
        curDate = curtime.strftime('%d')
        orgDate = orgtime.strftime('%d')
        if curDate == orgDate:
            result = 'Today'
        else:
            result = 'Yesterday'
    elif (int(diff.days) < 2):
        curDate = curtime.strftime('%d')
        orgDate = orgtime.strftime('%d')
        if int(curDate) > int(orgDate):
            if (int(curDate)-int(orgDate)) > 1:
                result = orgtime.strftime('%d%m%Y')
            else:
                result = 'Yesterday'
        else:
            result = 'Yesterday'
    else:
        result = orgtime.strftime('%d/%m/%Y')
    return result

def get_time_str(orgtime):
    result = orgtime.strftime('%H:%M')
    return result

def send_code_email(email,code):
    try:
        subject = 'Email Verify Code' 
        html_message = render_to_string('email/verify.html', {'code': code})
        plain_message = strip_tags(html_message)
        from_email = 'flickerface.com'
        send_mail(subject, plain_message, from_email, [email], html_message=html_message) 
        return True
    except:
        return False

def send_code_phone(phone,code):
    try: 
        # account_sid = "AC289ccc0193b7c525f221a6c1183410d5"
        # auth_token = "39b892bf7729a897cff9b83ef83bfc49"
        # client = Client(account_sid, auth_token)
        # verified_code = "Verify code from www.flickerface.com: " + code
        # message = client.messages \
        #     .create(
        #         body=verified_code,
        #         from_='+19382385325',
        #         to=phone
        #     )
        # print(phone)
        # print(message)
        return True
    except:
        return False

def get_user_attachs(request,user_post_id_array):    
    user = request.user
    attachs = []   
    if user.avatar:
        data = {}
        data['ext'] = user.avatar.url.split('.')[1]
        data['attach'] = user.avatar.url
        attachs.append(data)
        cnt_attachs = cnt_attachs + 1
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:8]
    else:
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:9]
    for item in attachstemp:
        data = {}
        data['ext'] = item.attachname.split('.')[1]
        data['attach'] = 'media/'+item.attachname
        attachs.append(data)
    return attachs

def login_custom(request):
    if not request.user.is_authenticated:
        return render(request,'registration/login.html')
    else:
        user = request.user
        if user.verified == "0":
            return redirect('/confirm')
        else:
            return redirect('/dashboard')
    

def register_custom(request):
    if not request.user.is_authenticated:
        return render(request,'registration/register.html') 
    else:
        user = request.user
        if user.verified == "0":
            return redirect('/confirm')
        else:
            return redirect('/dashboard')


def confirm(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    else:        
        return render(request,'registration/confirm.html') 


def index(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    else:        
        return redirect('/dashboard')

def trending(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    user = request.user  
    if user.verified == "0":
        return redirect('/confirm')
    
   
    users = []        
    users = get_users(request)
    followingusers = get_users_following(user.id)
    
    curuser = {}
    curuser = get_curuser(request,user.id)
    
    experience = Experience.objects.filter(user_id=user.id)
    education = Education.objects.filter(user_id=user.id)
    user_post_id_array = []
    user_posts = Posts.objects.filter(user_id=user.id)
    for item in user_posts:
        user_post_id_array.append(item.id)
    
    cnt_attachs = PostAttach.objects.filter(post_id__in=user_post_id_array).count()
    orgtime = datetime.datetime.now()
    get_different_time(orgtime)
    attachs = []   
    if user.avatar:
        data = {}
        data['ext'] = user.avatar.url.split('.')[1]
        data['attach'] = user.avatar.url
        attachs.append(data)
        cnt_attachs = cnt_attachs + 1
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:8]
    else:
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:9]
    for item in attachstemp:
        data = {}
        data['ext'] = item.attachname.split('.')[1]
        data['attach'] = 'media/'+item.attachname
        attachs.append(data)
    return render(request,'data/trending.html',{'users':users,'curuser':curuser,'followingusers':followingusers,'education':education,'experience':experience,'attachs':attachs,'cnt_attachs':cnt_attachs})     

def dashboard(request):
    
    user = request.user 
    if not request.user.is_authenticated:
        return redirect('/login')
    if user.verified == "0":
        return redirect('/confirm')
    
    if user.location:
        pass
    else:
        ipaddress = get_client_ip(request) 
        geo_info = get_geolocation_for_ip(ipaddress)
        results=json.dumps(geo_info) 
        results=json.loads(results)

        if results['country_name']:           
            address = results['country_name']
            user.location = address
            user.save()
    
   
    users = []        
    users = get_users(request)
    followingusers = get_users_following(user.id)
    
    curuser = {}
    curuser = get_curuser(request,user.id)
    
    experience = Experience.objects.filter(user_id=user.id)
    education = Education.objects.filter(user_id=user.id)
    user_post_id_array = []
    user_posts = Posts.objects.filter(user_id=user.id)
    for item in user_posts:
        user_post_id_array.append(item.id)
    
    cnt_attachs = PostAttach.objects.filter(post_id__in=user_post_id_array).count()
    orgtime = datetime.datetime.now()
    get_different_time(orgtime)
    attachs = []   
    if user.avatar:
        data = {}
        data['ext'] = user.avatar.url.split('.')[1]
        data['attach'] = user.avatar.url
        attachs.append(data)
        cnt_attachs = cnt_attachs + 1
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:8]
    else:
        attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:9]
    for item in attachstemp:
        data = {}
        data['ext'] = item.attachname.split('.')[1]
        data['attach'] = 'media/'+item.attachname
        attachs.append(data)
    return render(request,'data/dashboard.html',{'users':users,'curuser':curuser,'followingusers':followingusers,'education':education,'experience':experience,'attachs':attachs,'cnt_attachs':cnt_attachs}) 

def viewconnections(request,which):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    if user.verified == "0":
        return redirect('/confirm')
    if which in "following followers":
        following = get_following(request)
        followers = get_followers(request)
        return render(request,'data/viewconnections.html',{'which':which,'following':following,'followers':followers})
    else:
        return redirect('/viewconnections')

def viewconnection(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    if user.verified == "0":
        return redirect('/confirm')
    which = 'following'
    following = get_following(request)
    followers = get_followers(request)
    return render(request,'data/viewconnections.html',{'which':which,'following':following,'followers':followers})



# -------------------------------------------------------
def logout(request):
    if request.method == 'POST':
        auth_views.auth_logout(request)
    return redirect('/login')

def profile(request):    
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    
    if user.verified == "0":
        return redirect('/confirm')
       
    users = []      
    users = get_users(request)
    followers = Follows.objects.filter(who=user.id).count()   
    following = Follows.objects.filter(whom=user.id).count()
    experiences = Experience.objects.filter(user_id=user.id).order_by('-created_at')
    educations = Education.objects.filter(user_id=user.id).order_by('-created_at')

    attachstemp = PostAttach.objects.exclude(post_id=0).order_by('-created_at')[:9]
    attachs = []    
    for item in attachstemp:
        data = {}
        data['ext'] = item.attachname.split('.')[1]
        data['attach'] = item.attach
        attachs.append(data)
    return render(request,'data/profile.html',{'experiences':experiences,'educations':educations,'users':users,'followers':followers,'following':following,'attachs':attachs})

def editprofile(request):    
    if not request.user.is_authenticated:
        return redirect('/login')

    user = request.user
    experiences = Experience.objects.filter(user_id=user.id).order_by('-created_at')
    educations = Education.objects.filter(user_id=user.id).order_by('-created_at')
    return render(request,'data/editprofile.html',{'experiences':experiences,'educations':educations}) 

def faq(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request,'data/faq.html') 

def terms(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request,'data/terms.html') 

def privacy(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request,'data/privacy.html') 

def messages(request): 
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    
    if user.verified == "0":
        return redirect('/confirm')

    users= get_users(request)
    return render(request,'data/messages.html',{'users':users}) 

def notifications(request):

    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    
    if user.verified == "0":
        return redirect('/confirm')

    return render(request,'data/notifications.html') 


def company_profile(request):
    return render(request,'data/company_profile.html') 

def userposts(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    
    if user.verified == "0":
        return redirect('/confirm')
   
    users = []        
    users = get_users(request)
    followingusers = get_users_following(user.id)
    
    curuser = {}
    curuser = get_curuser(request,user.id)
    
    experience = Experience.objects.filter(user_id=user.id)
    education = Education.objects.filter(user_id=user.id)
    user_post_id_array = []
    user_posts = Posts.objects.filter(user_id=user.id)
    for item in user_posts:
        user_post_id_array.append(item.id)
    attachstemp = PostAttach.objects.filter(post_id__in=user_post_id_array).order_by('-created_at')[:9]
    cnt_attachs = PostAttach.objects.filter(post_id__in=user_post_id_array).count()
    orgtime = datetime.datetime.now()
    get_different_time(orgtime)

    attachs = []    
    attachs = get_user_attachs(request,user_post_id_array)

    return render(request,'data/userposts.html',{'users':users,'curuser':curuser,'followingusers':followingusers,'education':education,'experience':experience,'attachs':attachs,'cnt_attachs':cnt_attachs})   


def view_user_profile(request,username):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    
    if user.verified == "0":
        return redirect('/confirm')

    try:        
        user = request.user
        userstemp = CustomUser.objects.exclude(id=user.id)
        users = []         
        users = get_users(request)
        row = CustomUser.objects.get(username=username)
        curuser = {}
        curuser = get_curuser(request,row.id)       
        followingusers = get_users_following(user.id)
        experiences = Experience.objects.filter(user_id=row.id)
        educations = Education.objects.filter(user_id=row.id)       
        return render(request,'data/profileuser.html',{'users':users,'curuser':curuser,'followingusers':followingusers,'experiences':experiences,'educations':educations}) 
    except:
            return redirect('/dashboard')


# ajax_part

def upload_avatar(request):
    try:
        user = request.user
        is_store = request.POST.get('is_store') 
        if request.POST.get('is_cover'):
            user.back = request.FILES.get('attach')
            user.save()
        else: 
            if is_store == '1':                
                user.avatar = request.FILES.get('attach')
                user.save()
            else:                
                user.avatar = ''
                user.save()
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})
def store_aboutme(request):
    aboutme = request.POST.get('aboutme')
    user = request.user
    user.aboutme = aboutme
    user.save()    
    return JsonResponse({'response':True})

def store_sociallink(request):
    
    user = request.user
    user.linkInstagram = request.POST.get('linkInstagram')
    user.linkFacebook = request.POST.get('linkFacebook')
    user.linkTwitter = request.POST.get('linkTwitter')
    user.linkYoutube = request.POST.get('linkYoutube')
    user.linkGithub = request.POST.get('linkGithub')
    user.save()
    
    return JsonResponse({'response':True})

def store_basicinfo(request):    
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    phonecount = CustomUser.objects.filter(phone=phone).count()
    emailcount = CustomUser.objects.filter(email=email).count()
    user = request.user
    result={}
    
    if user.email == email:        
        emailcount = 0
    if user.phone == phone:        
        phonecount = 0
    result['phonecount'] = phonecount
    result['emailcount'] = emailcount
    if phonecount > 0 or emailcount > 0 :
        return JsonResponse({'response':result})
    else:  
        if request.POST.get('public_birth'):
            user.public_birth='1'
        else:
            user.public_birth='0'
        if request.POST.get('public_email'):
            user.public_email='1'
        else:
            user.public_email='0'
        if request.POST.get('public_phone'):
            user.public_phone='1'
        else:
            user.public_phone='0'
        user.email = email
        user.first_name = request.POST.get('fname')
        user.last_name = request.POST.get('lname')
        user.birthMonth = request.POST.get('birthMonth')
        user.birthDay = request.POST.get('birthDay')
        user.birthYear = request.POST.get('birthYear')
        user.gender = request.POST.get('gender')
        user.location = request.POST.get('location')       
        user.phone = request.POST.get('phone')
        user.jobtitle = request.POST.get('jobtitle')       
        user.company = request.POST.get('company')        
        user.save()
        
        return JsonResponse({'response':result})




def set_follow(request):
    try:
        user = request.user  
        id = request.GET.get('id')
        followed = Follows.objects.filter(who=user.id,whom=id)
        if followed : 
            followed.delete()
            if Room.objects.filter(who=user.id,whom=id):
                cur_room = Room.objects.get(who=user.id,whom=id)
                cur_room.status = '0'
                cur_room.updated_at = datetime.datetime.now()
                cur_room.save()
        else :        
            row = Follows(who=user.id,whom=id)
            row.save()            
                    
            if Room.objects.filter(who=user.id,whom=id) or Room.objects.filter(whom=user.id,who=id):
                if Room.objects.filter(who=user.id,whom=id):
                    is_room = Room.objects.get(who=user.id,whom=id)
                    is_room.status='1'
                    is_room.updated_at = datetime.datetime.now()
                    is_room.save()
            else:                
                room = Room(who=user.id,whom=id,accepted='0',status='1',updated_at=datetime.datetime.now())
                room.save()
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})

def store_experience(request):
    try:
        user = request.user 
        if request.GET.get('exp_id'):
            thisExp = Experience.objects.get(id=request.GET.get('exp_id'))
            thisExp.date_start = request.GET.get('from')
            thisExp.date_end = request.GET.get('to')
            thisExp.company = request.GET.get('company')
            thisExp.position = request.GET.get('position')
            thisExp.responsibilities = request.GET.get('responsibilities')
            thisExp.save()
        else: 
            row = Experience(user_id=user.id,title=request.GET.get('title'),date_start=request.GET.get('from'),date_end=request.GET.get('to'),company=request.GET.get('company'),position=request.GET.get('position'),responsibilities=request.GET.get('responsibilities'))
            row.save()
        
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})

def delete_experience(request):
    try:
        user = request.user  
        Experience.objects.get(id=request.GET.get('id')).delete()        
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})

def store_education(request):
    try:
        user = request.user  
        if request.GET.get('education_id'):
            thisEducation = Education.objects.get(id=request.GET.get('education_id'))
            thisEducation.date_start = request.GET.get('from')
            thisEducation.date_end = request.GET.get('to')
            thisEducation.school = request.GET.get('school')
            thisEducation.degree = request.GET.get('degree')
            thisEducation.save()
        else:
            row = Education(user_id=user.id,date_start=request.GET.get('from'),date_end=request.GET.get('to'),school=request.GET.get('school'),degree=request.GET.get('degree'))
            row.save()
        
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})

def delete_education(request):
    try:
        user = request.user  
        Education.objects.get(id=request.GET.get('id')).delete()        
        return JsonResponse({'response':True})
    except:
        return JsonResponse({'response':False})

def attachmentsview(request):
    return render(request,'data/viewattachs.html')

def get_attachs(request):
    currentPage = 1
    user = request.user
    userpostarraytemp = Posts.objects.filter(user_id=user.id)
    userpostarray = []
    for item in userpostarraytemp:
        userpostarray.append(item.id)        
    attachs = PostAttach.objects.exclude(post_id=0) & PostAttach.objects.filter(post_id__in=userpostarray).order_by('-created_at')

    pagenum = math.ceil(attachs.count()/PAGINATION_COUNT)
    paginator = Paginator(attachs,PAGINATION_COUNT)   
    resultscollection = paginator.get_page(currentPage) 
    results = []    
    for item in resultscollection:
        data = {}
        data['id'] = item.id
        data['ext'] = item.attachname.split('.')[1]
        data['attach'] = item.attachname
        results.append(data)
    return JsonResponse({'results':results,'pagenum':pagenum})

def check_login(request):
    email = request.POST.get('email').replace(" ", "")
    password = request.POST.get('password')
    which = request.POST.get('which')
    results = {}
    
    is_phone = 0
    is_email = 0
    if which == 'phone':
        is_phone = CustomUser.objects.filter(phone=email).count()
        if is_phone > 0:
            cur_user = CustomUser.objects.get(phone=email)
    else:
        is_email = CustomUser.objects.filter(email=email).count()
        if is_email > 0:
            cur_user = CustomUser.objects.get(email=email)
    
    results['is_phone'] = is_phone
    results['is_email'] = is_email
    results['is_pass'] = '1'
    results['is_active'] = '1'
    
    
    if is_phone == 0 and is_email == 0:        
        return JsonResponse({'results':results})
    else: 
        
        if cur_user.is_active:            
            user = authenticate(username=cur_user.username,password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'results':results})

            else:            
                results['is_pass'] = '0'
                return JsonResponse({'results':results})    
        else:            
            results['is_active'] = '0'
            return JsonResponse({'results':results}) 
            


# @api_view(['GET', 'POST', 'DELETE'])
# def check_rigister(request):
#     try: 
#         print("request============")
#         print(request)
#     except CustomUser.DoesNotExist: 
#         return JsonResponse({'message': 'The tutorial does not exist'}) 
    # GET list of tutorials, POST a new tutorial, DELETE all tutorials
@api_view(['GET', 'POST', 'DELETE'])
def check_register(request):
    userdata = JSONParser().parse(request)
    try:
        firstname = userdata['firstname']
        lastname = userdata['lastname']
        email = userdata['email']
        phone = userdata['phone']
        password = userdata['password']
        which = userdata['which']
        # birthDay = request.POST.get('birthDay')
        # birthMonth = request.POST.get('birthMonth')
        # birthYear = request.POST.get('birthYear')
        # gender = request.POST.get('gender')
        # phone_code = "+"+request.POST.get('phoneCode')
        if which == 'phone':
            is_phone = CustomUser.objects.filter(phone=phone).count()
            is_email = 0
        else:
            is_phone = 0
            is_email = CustomUser.objects.filter(email=email).count()

        already_results = {}
        results = {}
        already_results['is_phone'] = is_phone
        already_results['is_email'] = is_email
        already_results['which'] = which
        verified_code = str(random.randint(100000,999999))
        ipaddress = get_client_ip(request) 
        geo_info = get_geolocation_for_ip(ipaddress)
        results=json.dumps(geo_info) 
        results=json.loads(results)
        address = ''
        if results['country_name']:           
            address = results['country_name']  
        if is_phone > 0 or is_email > 0:
            return JsonResponse({'results':already_results})
        else:      
            if which == 'phone':
                # row = CustomUser(password=make_password(password),username=datetime.datetime.now().strftime("%m%d%Y%H%M%S"),is_superuser=0,is_staff=0,is_active=1,first_name=firstname,last_name=lastname,phone=phone,phone_code=phone_code,verified_with='p',verified_code=verified_code,birthDay=birthDay,birthMonth=birthMonth,birthYear=birthYear,gender=gender,location=address)
                row = CustomUser(password=make_password(password),username=datetime.datetime.now().strftime("%m%d%Y%H%M%S"),is_superuser=0,is_staff=0,is_active=1,first_name=firstname,last_name=lastname,phone=phone,verified_with='p',verified_code=verified_code,location=address)
                row.save()
                user = authenticate(username=row.username,password=password)
                login(request, user)
                send_code_phone(phone,verified_code)
            
            else:
                # row = CustomUser(password=make_password(password),username=datetime.datetime.now().strftime("%m%d%Y%H%M%S"),is_superuser=0,is_staff=0,is_active=1,first_name=firstname,last_name=lastname,email=email,verified_with='e',verified_code=verified_code,birthDay=birthDay,birthMonth=birthMonth,birthYear=birthYear,gender=gender,location=address)
                row = CustomUser(password=make_password(password),username=datetime.datetime.now().strftime("%m%d%Y%H%M%S"),is_superuser=0,is_staff=0,is_active=1,first_name=firstname,last_name=lastname,email=email,verified_with='e',verified_code=verified_code,location=address)
                print(row)
                row.save()  
                user = authenticate(username=row.username,password=password)
                login(request, user)
                send_code_email(email,verified_code)  
            subject = 'Welcome to FlickerFace world.'   
            body = 'You have successfully signed up. Setup your account for better view to your followers.'
            row_noti = Notification(user_id=row.id,subject=subject,body=body)
            row_noti.save()
            return JsonResponse({'results':results})
    except:
        return JsonResponse({'results':False})

def verify_confirm(request):
    results = False
    try:
        code = request.POST.get('code')
        user = request.user
        if(user.verified_code == code):
            user.verified = '1'
            user.save()
            results = True
        else:
            results = False
        return JsonResponse({'results':results,'auth':True})
    except:
        return JsonResponse({'results':results,'auth':False})

def verify_resend(request):
    results = False
    try:        
        user = request.user
        verified_code = str(random.randint(100000,999999))

        if(user.verified_with == 'e'):
            user.verified_code = verified_code            
            user.save()            
            send_code_email(user.email,verified_code) 
            results = True
        else:
            user.verified_code = verified_code            
            user.save() 
            phone = user.phone_code+user.phone
            send_code_phone(phone,verified_code)
            results = True        
        return JsonResponse({'results':results,'which':user.verified_with,'auth':True})
    except:
        return JsonResponse({'results':results,'which':"",'auth':False})

def get_new_notification(request):
    user = request.user
    results = []
    try:
        
        news = Notification.objects.filter(user_id=user.id,read='0').order_by('-created_at')
        if news:
            for item in news:
                data = {}
                data['id'] = item.id
                data['user_id'] = item.user_id
                data['subject'] = item.subject
                data['body'] = item.body
                data['post_id'] = ''
                data['group_id'] = ''
                data['page_id'] = ''
                data['created_at'] = get_different_time(item.created_at)
                thisUser = CustomUser.objects.get(id=item.user_id)
                if thisUser.avatar:
                    data['avatar'] = thisUser.avatar.url 
                else:
                    data['avatar'] = '/static/images/user.png'
                results.append(data)        
        return JsonResponse({'results':results})
    except:
        return JsonResponse({'results':results})

def get_notification(request):
    user = request.user
    results = []
    try:        
        news = Notification.objects.filter(user_id=user.id).order_by('-created_at')
        print(news)
        if news:
            for item in news:
                data = {}
                data['id'] = item.id
                data['user_id'] = item.user_id
                data['subject'] = item.subject
                data['body'] = item.body
                data['post_id'] = ''
                data['group_id'] = ''
                data['page_id'] = ''
                data['read'] = item.read
                data['created_at'] = get_different_time(item.created_at)
                thisUser = CustomUser.objects.get(id=item.user_id)
                if thisUser.avatar:
                    data['avatar'] = thisUser.avatar.url 
                else:
                    data['avatar'] = '/static/images/user.png'
                results.append(data)
        return JsonResponse({'results':results})
    except:
        return JsonResponse({'results':results})

def delete_notification(request):

    id = request.GET.get('id')
    try:
        Notification.objects.get(id=id).delete()
        return JsonResponse({'results':True})
    except:
        return JsonResponse({'results':False})

def notification_set_read(request):
    id = request.GET.get('id')
    try:
        thisNoti = Notification.objects.get(id=id)
        thisNoti.read = '1'
        thisNoti.save()
        return JsonResponse({'results':True})
    except:
        return JsonResponse({'results':False})

def get_searchresult(request):
    users = []
    user = request.user
    results=''
    search_word = request.GET.get('search_word')
    userstemp = CustomUser.objects.filter(first_name__contains=search_word)|CustomUser.objects.filter(last_name__contains=search_word)        
    
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = '/static/images/user.png'       
        if Follows.objects.filter(who=user.id,whom=item.id).count() :
            data['followed']='1'
        else :
            data['followed']='0'
        users.append(data)
    
    return JsonResponse({'results':users})


def get_UserForInvite(request):
    users = []
    user = request.user
    results=''
    
    search_word = request.GET.get('search_word')
    if search_word=="":
        userstemp = CustomUser.objects.exclude(id=user.id)
    else:
        userstemp = CustomUser.objects.filter(first_name__contains=search_word)|CustomUser.objects.filter(last_name__contains=search_word)        
    
    for item in userstemp:
        data = {}
        data['id'] = item.id
        data['username'] = item.username
        data['firstname'] = item.first_name
        data['lastname'] = item.last_name
        if item.avatar:
            data['avatar'] = item.avatar.url 
        else:
            data['avatar'] = '/static/images/user.png'      
        if Follows.objects.filter(who=user.id,whom=item.id).count() :
            data['followed']='1'
        else :
            data['followed']='0'
        users.append(data)
    
    return JsonResponse({'results':users})

def get_phoneCode(request):
    code = ''
    # ipaddress = get_client_ip(request) 
    ipaddress = '188.43.235.177'
    geo_info = get_geolocation_for_ip(ipaddress)
    results=json.dumps(geo_info) 
    results=json.loads(results)
    if results['country_code']:
        code = results['country_code']
    else:
        code = 'us'
    return JsonResponse({'results':code})

def close_account(request):
    user = request.user
    try:
        user.is_active = "0"
        user.save()
        auth_views.auth_logout(request)
        return JsonResponse({'results':True})
    except:
        return JsonResponse({'results':False})