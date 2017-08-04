from django.db import models
from django.contrib.auth.models import User
import re, uuid


class Profil(models.Model):
    user = models.OneToOneField(User, related_name='aprofile') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    # add some stuff
    
    
