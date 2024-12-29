from urllib import response
from django.http import HttpResponse
from rest_framework.response import Response
from . serializers import *
from rest_framework.decorators import api_view,permission_classes, throttle_classes, parser_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from . models import *
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.conf import settings 
from django.middleware import csrf
from rest_framework.parsers import MultiPartParser
import openpyxl


def home(request):
    return HttpResponse("Hi There! this is Home :)")


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register(request):
    if request.method =="POST":
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        else:
            return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = CustomLoginLogicSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.context['user']
        tokens = get_tokens_for_user(user)
        response = Response({"detail":"Login successful","data":serializer.validated_data},status=status.HTTP_200_OK)

        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=tokens["access"],
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )

        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value=tokens["refresh"],
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )

        # setting the csrf token cookie
        csrf_token = csrf.get_token(request)
        response.set_cookie('csrftoken', csrf_token, samesite='Lax')

        return response
    
    else:
        return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    response = Response({"detail":"logout successful"},status=status.HTTP_200_OK)
    response.delete_cookie('access_token') # clear my jwt token 
    response.delete_cookie('csrf_token') #clear the jwt token
    return response

@api_view(['GET','PUT','PATCH']) #PATCH is for testing purposes
@throttle_classes([UserRateThrottle])
def ProfileManager(request,pk):
    try:
        user_profile = UserProfile.objects.get(user_id=pk)
    except UserProfile.DoesNotExist:
        return Response({"detail":"Profile does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = UserProfileSerializer(user_profile)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method in ['PATCH','PUT']:
        partial = request.method == 'PATCH' # will validate to True if it is 
    serializer = UserProfileSerializer(user_profile,data=request.data,partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail":"Profile updated","data":serializer.data},status=status.HTTP_200_OK)
    else:
        return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET','POST'])
@throttle_classes([UserRateThrottle])
def EventScheduler(request):
    if request.method =="GET":
        events = Events.objects.all()
        count = events.count()
        if count == 0:
            return Response({"detail":"No events found"},status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = EventSerializer(events,many=True)
            return Response({"data":serializer.data},status=status.HTTP_200_OK)

    if request.method =='POST':
        serializer = EventSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},status=status.HTTP_201_CREATED)
        else:
            return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','PATCH','DELETE'])
@throttle_classes([UserRateThrottle])
def EventDetail(request,pk):
    try:
        event = Events.objects.get(id=pk)
    except Events.DoesNotExist:
        return Response({"detail":"Event not found"},status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = EventSerializer(event)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method =='DELETE':
        event.delete()
        return Response({"detail":"Event was deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
    if request.method in ['PATCH','PUT']:
        partial = request.method == 'PATCH' # will validate to True if it is 
        serializer = EventSerializer(event,data=request.data,partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
        
        else:
            return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET','POST'])
@throttle_classes([UserRateThrottle])
def Announcement(request):
    
    if request.method =='GET':
        announcements = Announcements.objects.all()
        count = announcements.count()
        if count == 0:
            return Response({"detail":"No announcements found"},status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = AnnouncementsSerializer(announcements,many=True)
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        serializer = AnnouncementsSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail":"Announcement added","data":serializer.data},status=status.HTTP_201_CREATED)
        else:
            return Response({
                "data":serializer.data,
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','PATCH','DELETE'])
@throttle_classes([UserRateThrottle])
def AnnouncementDetail(request,pk):
    try:
        announcement = Announcements.objects.get(id=pk)
    except Announcements.DoesNotExist:
        return Response({"detail":"Announcement not found"},status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = AnnouncementsSerializer(announcement)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method in ['PATCH','PUT']:
        partial = request.method == 'PATCH' # will validate to True if it is 
        serializer = AnnouncementsSerializer(announcement,data=request.data,partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail":"Announcement Updated","data":serializer.data},status=status.HTTP_200_OK)
        
        else:
            return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def profiles(request):
    user_profiles = UserProfile.objects.all()
    count = user_profiles.count()
    if count == 0:
        return Response({"No profiles found"},status=status.HTTP_204_NO_CONTENT)
    serializer = UserProfileSerializer(user_profiles,many=True)
    return Response({"data":serializer.data},status=status.HTTP_200_OK)
    

@api_view(['GET','PUT','PATCH']) #PATCH is for testing purposes 
@permission_classes([AllowAny])
def SchoolProfileManager(request,pk):
    try:
        school_profile = SchoolProfile.objects.get(user_id=pk)
    except SchoolProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = SchoolProfileSerializer(school_profile)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method in ['PATCH','PUT']:
        partial = request.method == 'PATCH' # will validate to True if it is 
    serializer = SchoolProfileSerializer(school_profile,data=request.data,partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    else:
        return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET','POST'])
def SubClasses_me(request):
    if request.method =='GET':
        my_subclasses = SubClasses.objects.all()
        serializer = subclassesSerializer(my_subclasses,many=True)
        if my_subclasses.count() == 0:
            return Response({"detail":"No subclasses found"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        serializer = subclassesSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail":"Subclass was successfully created"},status=status.HTTP_201_CREATED)
        else:
            return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST','GET'])
def StudentCreator(request):
    if request.method =='POST':
        serializer = AddStudentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},status=status.HTTP_201_CREATED)
        else:
            return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    if request.method =='GET':
        students = Student.objects.all()
        count = students.count()
        if request.method =='GET':
            if count == 0:
                return Response({"detail":"No students found"},status=status.HTTP_404_NOT_FOUND)
            serializer = StudentSerializer(students,many=True)
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
    

@api_view(['GET','PUT','PATCH','DELETE'])
def StudentDetail(request,pk):
    try:
        student = Student.objects.get(user_id=pk)
    except Student.DoesNotExist:
        return Response({"detail":"Student not found"},status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = StudentSerializer(student)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    if request.method =='DELETE':
        student.delete()
        return Response({"detail":"Student was deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
    if request.method in ['PATCH','PUT']:
        partial = request.method == 'PATCH' # will validate to True if it is 
        serializer = StudentSerializer(student,data=request.data,partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
        
        else:
            return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
@parser_classes([MultiPartParser])
def ImportExport(request):
    if 'file' not in request.FILES:
        return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    try:
        # Load the Excel workbook
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active  # Assuming data is in the first sheet

        errors = []
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):  # Skip header row
            data = {
                "first_name": row[0],
                "last_name": row[1]
            }

            # Validate and save data using the serializer
            serializer = StudentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                errors.append({"row": row_num, "errors": serializer.errors})

        # Check for errors
        if errors:
            return Response({"message": "Some rows failed to import.", "errors": errors},status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Users imported successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@parser_classes([MultiPartParser])
def ImportStudents(request):
    if 'file' not in request.FILES:
        return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    try:
        # Load the Excel workbook
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active  # Assuming data is in the first sheet

        data_list = []
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):  # Skip header row
            data_list.append({"first_name": row[0], "last_name": row[1]})

        # Validate and save data using the serializer
        serializer = AddStudentSerializer(data=data_list, many=True)
        if serializer.is_valid():
            # Bulk create the users
            users = serializer.save()

            # Create profiles for each user
            for user in users:
                UserProfile.objects.create(user=user)
                Student.objects.create(user=user)

            return Response({"message": "Students imported successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"Some rows failed validation. {row_num}", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)