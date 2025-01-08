from django.db import models
import datetime
import datetime
from frontline.models import CustomUser




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