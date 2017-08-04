from django.shortcuts import redirect, HttpResponseRedirect, get_object_or_404, render
from django.http import HttpResponse
from django.views import View
from users.models import Profil
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from users.forms import RegistrationForm, SignInForm, ChangePassForm, EmailNewPass
import hashlib, random, string
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def logout_view(request):
    logout(request)
    return redirect('/') 

def register_page(request):
    email_taken = False
    username_taken = False
    if request.user.is_authenticated():
        return render(request, 'home.html')
    registration_form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            datas={}
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                username_taken = True
                return render(request, 'register_page.html', {'form':registration_form,'username_taken': username_taken})
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                email_taken = True
                return render(request, 'register_page.html', {'form':registration_form,'email_taken': email_taken})
            datas['username']=form.cleaned_data['username']
            datas['email']=form.cleaned_data['email']
            datas['password1']=form.cleaned_data['password1']
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            usernamesalt = datas['email']
            if isinstance(usernamesalt, str):
                usernamesalt=str.encode(usernamesalt)
            if isinstance(salt, str):
                salt=str.encode(salt)
            #print(salt)
            #print(usernamesalt)
            datas['activation_key']=hashlib.sha1(salt+usernamesalt).hexdigest()
            datas['email_path']="/home/connlloc/sites/mc/static/ActivationEmail.txt"
            datas['email_subject']="activate your account"
            form.sendEmail(datas) #Send validation email
            form.save(datas) #Save the user and his profile
            request.session['registered']=True #For display purposes
            return render(request, 'register_page.html', {'email_sent':True})
        else:

            registration_form = form #Display form with error messages (incorrect fields, etc
    return render(request, 'register_page.html', {'form':registration_form})




def activation(request, key):
    activation_expired = False
    already_active = False
    profil = get_object_or_404(Profil, activation_key=key)
    if profil.user.is_active == False:
        now = timezone.now()
        if now > profil.key_expires:
            activation_expired = True #Display : offer to user to have another activation link (a link in template sending to the view new_activation_link)
            id_user = profil.user.username
            
        else: #Activation successful
            profil.user.is_active = True
            profil.user.save()
            id_user = None
    #If user is already active, simply display error message
    else:
        id_user = None
        already_active = True #Display : error message
    return render(request, 'activation.html', {'activation_expired':activation_expired,'already_active':already_active,'id_user':id_user})#need to fix this

def new_activation_link(request, user_id):# check if it's the same user and if they are already authed # new email not being sent
    form = RegistrationForm()
    datas={}
    user = User.objects.get(username=user_id)
    if user is not None and not user.is_active:#here
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="/home/connlloc/sites/mc/static/ResendEmail.txt"
        datas['email_subject']="Welcome to trendpinger"

        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        usernamesalt = datas['email']
            
        if isinstance(usernamesalt, str):
            usernamesalt=str.encode(usernamesalt)
        if isinstance(salt, str):
            salt=str.encode(salt)
        datas['activation_key']= hashlib.sha1(salt+usernamesalt).hexdigest()

        profil = Profil.objects.get(user=user)
        profil.activation_key = datas['activation_key']
        profil.key_expires=timezone.now() + datetime.timedelta(days=1)
        # generate public child from wallet file here 
        profil.save()

        form.sendEmail(datas)
        request.session['new_link']=True #Display : new link send
        return render(request, 'register_page.html', {'email_sent':True})
    else:
        return render(request, 'home.html')

def reset_password(request): #send email with new password set new password, check if email exists 
    email_new_pass = EmailNewPass()
    form = EmailNewPass(request.POST)
    if request.method == 'POST' and form.is_valid():
   
        if User.objects.filter(email=form.cleaned_data['email']).exists() == False:
            email_invalid = True
            return render(request,'passwordsent.html',{'form':email_new_pass, 'email_invalid': email_invalid})
        N = 12
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        u = User.objects.get(email=form.cleaned_data['email'])
        u.set_password(password)
        u.save()
        send_mail('new password', 'hello, please log with this password and change it http://trendpinger.com/change_password/:' + password , 'gonnellcough@gmail.com', [form.cleaned_data['email']], fail_silently=False)
        success = True
        return render(request,'passwordsent.html',{'success': success})
    
    else: 
        return render(request,'passwordsent.html',{'form':email_new_pass})

def sign_page(request):
    disabled_account = False
    incorrect_pass_or_username = False    
    if request.user.is_authenticated():
        return render(request, 'sign_in.html')
    sign_in_form = SignInForm()
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            datas={}
            datas['username']=form.cleaned_data['username']
            datas['password1']=form.cleaned_data['password1']
            user = authenticate(username=datas['username'], password=datas['password1'])
            if user is not None:
    # the password verified for the user
                if user.is_active:
                    #print("User is valid, active and authenticated")
                    login(request, user)
                    #profil = Profil.objects.get(user=request.user)
                    return redirect('/user-view/')
                else:
                    disabled_account = True
                    #print("The password is valid, but the account has been disabled! you may need to verify email")
            else:
    # the authentication system was unable to verify the username and password
                #print("The username or password were incorrect.")
                incorrect_pass_or_username = True
    return render(request, 'sign_in.html', {'form':sign_in_form, 'disabled_account': disabled_account, 'incorrect':incorrect_pass_or_username})#add error messages here!!!! 


@login_required(login_url='/sign_page/')
def change_password(request):
    successful = False
    form = ChangePassForm(request.POST)
    if request.user.is_authenticated() and request.method == 'POST' and form.is_valid():# if password is correct for user, change to new password

 
        datas = {}
        datas['password1']=form.cleaned_data['password1']
        datas['password2']=form.cleaned_data['newpassword1']
        datas['password3']=form.cleaned_data['newpassword2']
        if request.user.check_password(datas['password1']) == True and datas['password2'] == datas['password3']:
            request.user.set_password(datas['password2'])
            successful = True
            request.user.save()
            return render(request, 'change_password.html',{'form':form,'successful':successful})
        elif request.user.check_password(datas['password1']) == False:
            incorrect_pass = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'incorrect_pass':incorrect_pass})
        else:
            passwords_mismatch = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'passwords_mismatch':passwords_mismatch})            
    else:
        change_pass_form = ChangePassForm()
        return render(request, 'change_password.html',{'form':change_pass_form})# get error messages to work

