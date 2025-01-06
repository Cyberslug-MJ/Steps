from email.policy import default
import uuid
from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password as vp
from rest_framework.exceptions import ValidationError
import re
import secrets
import string


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=(("Admin","Admin"),("Parent","Parent"),("Teacher","Teacher")))
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','role','password']

    #CHECK  THE EMAIL 
    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use")
        return value

    def validate_password(self, value):
        try:
            vp(value)  # Uses Django's built-in validators
        except ValidationError as e:
            raise serializers.ValidationError({"password":list(e.messages)})
        return value
    
    def validate(self, attrs):
        # Manually validate password since validate_<field> methods are isolated
        self.validate_password(attrs.get('password'))
        return super().validate(attrs)

    def create(self,validated_data):

        unique_id = uuid.uuid4().hex[:6] # this generates a short unique id
        username = f"user_{unique_id}"

        while CustomUser.objects.filter(username=username).exists():
            unique_id = uuid.uuid4().hex[:6]
            username = f"user_{unique_id}"


        user = CustomUser(
        first_name = validated_data['first_name'],
        last_name = validated_data['last_name'],
        email = validated_data['email'],
        role = validated_data['role'],
        username = username
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.URLField()
    firstname = serializers.CharField(max_length=100)
    lastname = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False,read_only=True)
    address = serializers.CharField(max_length=255,required=False)


    class Meta:
        model = UserProfile
        fields = ['profile_picture','firstname','lastname','email','address']

    def update(self, instance, validated_data):
        # Updates the fields if data is provided and fills them with the old data if none is
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
    

class AnnouncementsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=128)
    body = serializers.CharField(max_length=150)
    audiences = serializers.ChoiceField(choices=(
    ("PR","Parents"),
    ("TC","Teachers"),
    ("ST","Students"),
    ("EV","Everyone"),
    ))

    class Meta:
        model = Announcements
        fields = ['id','title','body','audiences']
    

    def validate_title(self,value):
        if Announcements.objects.filter(title=value).exists():
            raise serializers.ValidationError("Title is not available")
        return value
    
    def create(self,validated_data):
        return super().create(validated_data)


class EventSerializer(serializers.ModelSerializer):
    tags =  (
        ("examination", "Examination"),
        ("holiday", "Holiday"),
        ("meeting", "Meeting"),
        ("extracurricular", "Extracurricular"),
        ("workshop", "Workshop"),
        ("graduation", "Graduation"),
        ("festival", "Festival"),
    )
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    event_tags = serializers.ChoiceField(choices=tags)
    start_time = serializers.DateTimeField(default=datetime.datetime.now)
    end_time = serializers.DateTimeField(default=datetime.datetime.now)
    location = serializers.CharField(max_length=100)

    class Meta:
        model = Events 
        fields = '__all__'

    def validate_name(self,value):
        if Events.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Event name, {value} is already in use")
        return value
    
    def validate_start_time(self,value):
        if Events.objects.filter(start_time=value).exists():
            raise serializers.ValidationError(f"There is an event already scheduled at {value}")
        return value
    
    def create(self,validated_data):
        return super().create(validated_data)


class CustomLoginLogicSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate(self, data):
        email = data['email']
        password = data['password']

        user = authenticate(email=email, password=password)
        
        if user.verified == True:
            self.context['authorization'] = 'Authorized'
        else:
            self.context['authorization'] = 'Unauthorized'

        if user is not None:

            data.pop('email',None)
            data.pop('password',None)
            data['role'] = user.role 
            data['school'] = user.school_name 
            data['user_id'] = user.id

            self.context['user'] = user  # Store user for potential use in the view

            return data
            
    
        else:
            raise serializers.ValidationError("Invalid credentials provided")
        

class SchoolProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    logo = serializers.URLField()
    pricing = serializers.CharField(read_only=True)
    subdomain_url = serializers.URLField(read_only=True)

    class Meta:
        model = SchoolProfile
        fields = ['name','logo','theme','pricing','subdomain_url']


    def validate_name(self,value):
        if SchoolProfile.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Sorry, {value} is not available")
        return value


    def create(self,validated_data):
        return super().create(validated_data)
    

class subclassesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    order = serializers.IntegerField()
    supervisors = serializers.PrimaryKeyRelatedField(
        queryset = Staff.objects.all(),
        many = True,
        required = False
    )

    def validate_name(self,value):
        if SubClasses.objects.filter(name=value).exists():
            raise serializers.ValidationError("A subclass with the same name already exists")
        return value

    class Meta:
        model = SubClasses
        fields = ['id','name','order','supervisors']
    
    def create(self,validated_data):
        staff = validated_data.pop('supervisors',[])
        subclass = SubClasses.objects.create(**validated_data)
        subclass.supervisors.set(staff)
        return subclass
    

class AddStudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name']

    def create(self,validated_data):

        unique_id = uuid.uuid4().hex[:6] # this generates a short unique id
        username = f"user_{unique_id}"
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

        while CustomUser.objects.filter(username=username).exists():
            unique_id = uuid.uuid4().hex[:6]
            username = f"user_{unique_id}"

        user = CustomUser(
        first_name = validated_data['first_name'],
        last_name = validated_data['last_name'],
        email = f'{username}@gmail.com',
        role = "Student",
        username = username
        )
        user.set_password(password)
        user.save()
        return user

    

class StudentSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    my_passkey = serializers.CharField(read_only=True)
    student_class = serializers.PrimaryKeyRelatedField(
        queryset = SubClasses.objects.all(),
        required = False
    )
    last_active = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Student
        exclude = ['fullname']


class StudentClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    order = serializers.IntegerField()
    created = serializers.DateField(read_only=True)
    modified = serializers.DateField(read_only=True)

    def validate_name(self,value):
        if StudentClasses.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Class with the same name already exists")
        return value
    
    def validate_order(self,value):
        if StudentClasses.objects.filter(order=value).exists():
            raise serializers.ValidationError("This order has already been assigned to a class")
        return value
        
    def create(self, validated_data):
        return super().create(validated_data)
    
    class Meta:
        model = StudentClasses
        fields = ['id','name','created','modified']


class AcademicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=105)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField(default=False)
    
    class Meta:
        model = Academic
        fields = ['name','start_date','end_date','is_active']
    
    def validate_name(self,value):
        if Academic.objects.filter(name=value).exists():
            raise serializers.ValidationError("Name already exists!")
        return value
    
    def create(self, validated_data):
        return super().create(validated_data)
    

class SubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    classes = serializers.PrimaryKeyRelatedField(
        queryset = SubClasses.objects.all(),
        many = True,
        required = False
    )
    supervisors = serializers.PrimaryKeyRelatedField(
        queryset = Staff.objects.all(),
        many = True,
        required = False
    )
    added = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Subjects
        fields = ['id','name','classes','supervisors','added','modified']

    def validate_name(self,value):
        if Subjects.objects.filter(name=value).exists():
            raise serializers.ValidationError("The name is already in use")
        return value
    

    def create(self, validated_data):
        class_data = validated_data.pop('classes',[])
        staff_data = validated_data.pop('supervisors',[])
        subject = Subjects.objects.create(**validated_data)
        subject.classes.set(class_data)
        subject.supervisors.set(staff_data)
        return subject
    
    

class StaffSerializer(serializers.ModelSerializer):
    added = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'


class RoleBasedSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    role = serializers.ChoiceField(choices=(("Student","Student"),("Parent","Parent"),("Teacher","Teacher")))
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','role','password']
    
    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use!")
        return value

    def validate_password(self,value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty")
        return value
    
    def validate_role(self,value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty")
        return value
    
    def create(self,validated_data):
        
        if validated_data['role'] == "Teacher":
            approval_status = True
        else:
            approval_status = False

        request = self.context['request']
        if request.user.is_anonymous:
            school = "King Edward Preparatory School"
        else:
            school = request.user.school_name            

        #school_name_context = request.user.school_name

        unique_id = uuid.uuid4().hex[:6] # this generates a short unique (UUID)
        username = f"user_{unique_id}"

        while CustomUser.objects.filter(username=username).exists():
            unique_id = uuid.uuid4().hex[:6]
            username = f"user_{unique_id}"

        
        user = CustomUser(
        first_name = validated_data['first_name'],
        last_name = validated_data['last_name'],
        email = validated_data['email'],
        role = validated_data['role'],
        username = username,
        approved = approval_status,
        school_name = school
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    date_added = serializers.DateTimeField(source="date_joined",read_only=True)
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','role','date_added']
    

class ParentSerializer(serializers.ModelSerializer):
    wards = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Student.objects.all()
    )
    class Meta:
        model = Parents
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset = Student.objects.all()
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset = Subjects.objects.all()
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset = Academic.objects.all()
    )
    class Meta:
        model = Assessment_records
        fields = '__all__'

    def create(self, validated_data):
        record = Assessment_records.objects.create(**validated_data)
        return record
    

class ApprovalsSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(read_only=True)
    lastname = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    class Meta:
        model = Approvals
        fields = ['id','firstname','lastname','email','approved','added','modified']
