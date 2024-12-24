from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.text import slugify
from django.conf import settings
import datetime


class CustomUserManager(BaseUserManager):

    def create_user(self, email, role, password=None):
        if not email:
            raise ValueError("Users must have an email address!")
        
        if not role:
            raise ValueError("Users must select a role")
        
        user = self.model(
            email = self.normalize_email(email),
            role = role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, role, password):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            role = role,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user



class CustomUser(AbstractBaseUser,PermissionsMixin):
    email           =models.EmailField(verbose_name='email',max_length=60,unique=True)
    username        =models.CharField(verbose_name='username',max_length=60,unique=True,blank=True)
    date_joined     =models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login      =models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin        =models.BooleanField(default=False)
    is_active       =models.BooleanField(default=True)
    is_superuser    =models.BooleanField(default=False)
    is_staff        =models.BooleanField(default=False)
    role_choices    =(("Admin","Admin"),("Parent","Parent"),("Student","Student"),("Teacher","Teacher"))
    role            =models.CharField(max_length=7,choices=role_choices,db_index=True)
    school_name     =models.CharField(max_length=200,blank=True,db_index=True,null=True)
    first_name      =models.CharField(verbose_name='first_name',max_length=200,blank=True)
    last_name       =models.CharField(verbose_name='last_name',max_length=200,blank=True)
    approved        =models.BooleanField(verbose_name='approved',default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role',]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    

    def has_module_perms(self,app_label):
        return True
    
    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUser'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    

    def get_short_name(self):
        return self.first_name
    

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True,verbose_name='User Profile',related_name='profile')
    profile_picture = models.URLField(default="https://my-bucket.s3.amazonaws.com/my-folder/my-image.jpg?AWSAccessKeyId=EXAMPLE&Expires=1672531199&Signature=abcdef",
    verbose_name="profile picture",blank=True,max_length=1000)
    firstname = models.CharField(max_length=100,blank=True)
    lastname = models.CharField(max_length=100,blank=True)
    email = models.EmailField(editable=False)
    address = models.CharField(max_length=255,blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'User Profile'

    def save(self, *args, **kwargs):
        user = self.user
        user.first_name = self.firstname
        user.last_name = self.lastname
        user.email = self.email
        user.save()
        super().save(*args, **kwargs)


class Events(models.Model):
    tags =  (
        ("examination", "Examination"),
        ("holiday", "Holiday"),
        ("meeting", "Meeting"),
        ("extracurricular", "Extracurricular"),
        ("workshop", "Workshop"),
        ("graduation", "Graduation"),
        ("festival", "Festival"),
    )
    name = models.CharField(unique=True,max_length=100)
    description = models.TextField(max_length=100)
    event_tags = models.CharField(choices=tags,max_length=15)
    start_time = models.DateTimeField(default=datetime.datetime.now)
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100,blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Events"
    
    def __str__(self):
        return self.name
    

class Announcements(models.Model):
    audience = (
    ("Parents","Parents"),
    ("Teachers","Teachers"),
    ("Students","Students"),
    ("Everyone","Everyone"),
    )
    LEVEL = (
        ("1","1"),
        ("2","2"),
        ("3","3")
    )
    title = models.CharField(max_length=128)
    body = models.TextField(max_length=150)
    audiences = models.CharField(max_length=8,choices=audience,default="Everyone")
    scheduled_for = models.DateField(default=datetime.datetime.now)
    priority = models.CharField(max_length=1,choices=LEVEL,verbose_name='priority',default="1")
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return self.title