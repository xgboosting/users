
from django import forms
from django.core.validators import EmailValidator, URLValidator
from django.template import Context, Template
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from users.models import Profil
import datetime
from django.utils import timezone
import re 
from django.core.exceptions import ValidationError
#from nocaptcha_recaptcha.fields import NoReCaptchaField


class RegistrationForm(forms.Form):
    username = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'username','class':'form-control input-perso'}),max_length=30,min_length=3)#,validators=[isValidUsername, validators.validate_slug])
    email = forms.EmailField(required=True,label="",widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control input-perso','id':'email_input'}),max_length=100,error_messages={'invalid': ("Email invalid")},validators=[EmailValidator])
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password1'}))
    password2 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'confirm password','class':'form-control input-perso','id':'password2'}))
    #captcha = NoReCaptchaField()



    #Override of clean method for password check
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

    #Override of save method for saving both User and Profil objects
    def save(self, datas):
        u = User.objects.create_user(datas['username'],
                                     datas['email'],
                                     datas['password1'])
        
        u.is_active = False
        u.save()
        profil=Profil()
        profil.user=u
        profil.activation_key=datas['activation_key']
        profil.key_expires=timezone.now() + datetime.timedelta(days=1)
        
        profil.save()
        return u

    #Handling of activation email sending ------>>>!! Warning : Domain name is hardcoded below !!<<<------
    #I am using a text file to write the email (I write my email in the text file with templatetags and then populate it with the method below)
    def sendEmail(self, datas):
        link="http://trendpinger.com/activate/"+datas['activation_key']
        c=Context({'activation_link':link,'email':datas['email']})
        f = open(datas['email_path'], 'r')
        t = Template(f.read())
        f.close()
        message=t.render(c)
        #print unicode(message).encode('utf8')
        
        send_mail(datas['email_subject'], message, 'con@bl4btc.io', [datas['email']], fail_silently=False)


class SignInForm(forms.Form):
    username = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'username','class':'form-control input-perso'}),max_length=30,min_length=3)#,validators=[isValidUsername, validators.validate_slug])
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input'}))
    #captcha = NoReCaptchaField()

class ChangePassForm(forms.Form):
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input1'}))
    newpassword1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input2'}))
    newpassword2 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input3'}))
    #captcha = NoReCaptchaField()


class EmailNewPass(forms.Form):
    email = forms.EmailField(required=True,label="",widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control input-perso','id':'email_input'}),max_length=100,error_messages={'invalid': ("Email invalid")},validators=[EmailValidator])
    #captcha = NoReCaptchaField()
