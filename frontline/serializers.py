import uuid
from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password as vp
from rest_framework.exceptions import ValidationError


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','password']

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
        email = validated_data['email'],
        role = "Admin",
        username = username
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class loginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254,write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email','password']
    

    def validate(self,data):
        email = data['email']
        password = data['password']

        user = authenticate(email=email,password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            data.pop('email',None)
            data.pop('password',None)
            data["refresh_token"] = str(refresh)
            data["access_token"] = str(refresh.access_token)
            data['role'] = user.role 
            data['school'] = user.school_name 
            data['user_id'] = user.id

            return data 

        else:
            raise serializers.ValidationError("Invalid credentials provided")
        

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
    scheduled_for = serializers.DateField(default=datetime.datetime.now)

    class Meta:
        model = Announcements
        fields = ['id','title','body','audiences','scheduled_for']
    

    def validate_title(self,value):
        if Announcements.objects.filter(title=value).exists():
            raise serializers.ValidationError("Title is not available")
        return value
    
    def validate_scheduled_for(self,value):
        if Announcements.objects.filter(scheduled_for=value).exists():
            raise serializers.ValidationError("An event has already been scheduled for that time")
        return value
    
    def create(self,validated_data):
        announcement = Announcements(
            title = validated_data['title'],
            body = validated_data['body'],
            audiences = validated_data['audiences'],
            scheduled_for = validated_data['scheduled_for']
        )
        return announcement


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
        event = Events(
            name = validated_data['name'],
            description = validated_data['description'],
            event_tags = validated_data['event_tags'],
            start_time = validated_data['start_time'],
            end_time = validated_data['end_time'],
            location = validated_data['location']
        )
        event.save()
        return event