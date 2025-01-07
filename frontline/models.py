from re import S
from timeit import default_timer
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.text import slugify
from django.conf import settings
import datetime
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
    verified        =models.BooleanField(default=False)


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
    firstname = models.CharField(max_length=200,blank=True)
    lastname = models.CharField(max_length=200,blank=True)
    email = models.EmailField(editable=False)
    address = models.CharField(max_length=150,blank=True)

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
    description = models.TextField(max_length=180)
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
    priority = models.CharField(max_length=1,choices=LEVEL,verbose_name='priority',default="1")
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return self.title
    

class SchoolProfile(models.Model):
    pricing_choices = (
        ("Basic","Basic"),
        ("Pro","Pro"),
        ("Enterprise","Enterprise")
    )
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True,related_name="school",verbose_name="school profile")
    name = models.CharField(max_length=255,blank=True)
    logo = models.URLField(default="https://my-bucket.s3.amazonaws.com/my-folder/my-image.jpg?AWSAccessKeyId=EXAMPLE&Expires=1672531199&Signature=abcdef",
    verbose_name="logo",blank=True,max_length=1000)
    pricing = models.CharField(choices=pricing_choices,max_length=10)
    subdomain_url = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.pricing} plan"

    def save(self, *args, **kwargs):

        #syncing user data 
        user = self.user
        user.school_name = self.name
        user.save()
        super(SchoolProfile, self).save(*args, **kwargs)


class Academic(models.Model):
    name = models.CharField(verbose_name='Academic Year',max_length=105,unique=True)
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        if self.is_active == True:
            return f"{self.name} - Active"
        else:
            return self.name

    def save(self, *args, **kwargs): 
        if self.is_active: 
            Academic.objects.filter(is_active=True).update(is_active=False) # Deactivate any other instances that are active
        super().save(*args, **kwargs)


class StudentClasses(models.Model):
    name = models.CharField(max_length=50,unique=True)
    Grade = models.ForeignKey('SubClasses',on_delete=models.CASCADE,verbose_name='associated grade',null=True,blank=True,default=1)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = "student classes"


class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='staff')
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200,default='',blank=True)
    added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField()

    def __str__(self):
        return self.user.get_full_name()
    
    class Meta:
        verbose_name_plural = 'staff'
        
    def save(self, *args, **kwargs):
        user = self.user
        self.fullname = user.get_full_name()
        self.firstname = user.first_name
        self.lastname = user.last_name
        self.last_active = user.last_login
        user.date_joined = self.added
        super(Staff, self).save(*args, **kwargs)


class SubClasses(models.Model):
    name = models.CharField(max_length=100,unique=True)
    order = models.PositiveIntegerField(unique=True,default=1)
    supervisors = models.ManyToManyField(Staff,related_name="supervisors",blank=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created",editable=False)
    last_modified = models.DateTimeField(auto_now=True, verbose_name="last modified",editable=False)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='student')
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200,default='',blank=True)
    student_class = models.ForeignKey(SubClasses,on_delete=models.CASCADE,verbose_name='Student class',blank=True,null=True)
    my_passkey = models.CharField(max_length=10,blank=True)
    added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        user = self.user
        self.fullname = user.get_full_name()
        self.firstname = user.first_name
        self.lastname = user.last_name
        self.last_active = user.last_login
        user.date_joined = self.added
        super(Student, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Students"


def get_active_academic():
    try:
        return Academic.objects.get(is_active=True)
    except Academic.DoesNotExist:
        return None


class Parents(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='parent')
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200,default='',blank=True)
    wards = models.ManyToManyField(Student,blank=True)
    added = models.DateTimeField(editable=False,auto_now_add=True)
    last_active = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True,editable=False)

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        user = self.user
        self.fullname = user.get_full_name()
        self.firstname = user.first_name
        self.lastname = user.last_name
        self.last_active = user.last_login
        user.date_joined = self.added
        super(Parents, self).save(*args, **kwargs)


class Attendance(models.Model):
    status_choices = (("Absent","Absent"),("Present","Present"))
    date = models.DateField(default=datetime.date.today,db_index=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE,verbose_name='student',db_index=True)
    status = models.CharField(max_length=7,choices=status_choices)
    academic_calendar = models.ForeignKey(Academic,on_delete=models.RESTRICT,verbose_name='calendar',default=get_active_academic)

    def __str__(self):
        return self.student.user.get_full_name()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'student', 'academic_calendar'],
                name='unique_attendance_per_student_per_date'
            )
        ]


class Approvals(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,verbose_name='user',related_name='approvals')
    firstname = models.CharField(max_length=200,default='')
    lastname = models.CharField(max_length=200,default='')
    email = models.EmailField(editable=False)
    approved = models.BooleanField()
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Approvals'

    def __str__(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        user = self.user
        if user.approved != self.approved:
            user.approved = self.approved
            user.save(update_fields=['approved'])
        super(Approvals, self).save(*args, **kwargs)


    
class Subjects(models.Model):
    name = models.CharField(verbose_name='name of subject',max_length=100,unique=True)
    classes = models.ManyToManyField(SubClasses,verbose_name="Classes")
    supervisors = models.ManyToManyField(Staff,blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "subjects"


class Assessment_records(models.Model):
    student = models.ForeignKey(Student,on_delete=models.RESTRICT,verbose_name='student')
    subject = models.ForeignKey(Subjects,on_delete=models.RESTRICT,verbose_name="subject")
    exams_score = models.PositiveIntegerField(verbose_name="Exams Score")
    class_score = models.PositiveIntegerField(verbose_name="Class Score")
    total_score = models.PositiveIntegerField(verbose_name="Total Score",blank=True)
    academic_year = models.ForeignKey(Academic,on_delete=models.RESTRICT,verbose_name='academic year',default=get_active_academic)
    grade = models.CharField(max_length=100,blank=True,editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject','academic_year'],
                name='Student Must have a unique assessment subject and academic year'
            )
        ]

        verbose_name_plural = "Assessment Records"

    def __str__(self):
        return self.student.user.get_full_name()


    def save(self, *args, **kwargs):
        self.total_score = self.class_score + self.exams_score
        super(Assessment_records, self).save(*args, **kwargs)


class MailChange(models.Model):
  user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mail_change_history')
  old_email = models.EmailField(max_length=255)
  new_email = models.EmailField(max_length=255)
  is_verified = models.BooleanField(default=False)
  verification_token = models.CharField(max_length=64)
  last_changed = models.DateField(auto_now=True)

  def __str__(self):
      return self.user.get_full_name()



class Transactions(models.Model):
    pass