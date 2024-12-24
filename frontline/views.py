from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from . serializers import *
from rest_framework.decorators import api_view,permission_classes, throttle_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from . models import *
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


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
            return Response({"detail":"User was created successfully"},status=status.HTTP_200_OK)

        else:
            return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def login(request):
    serializer = loginSerializer(data = request.data,context={"request":request})
    if serializer.is_valid():
        return Response({"data":serializer.validated_data},status=status.HTTP_200_OK)
    
    else:
        return Response({"data":serializer.data,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

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