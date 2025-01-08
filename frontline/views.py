from django.http import HttpResponse
from rest_framework.response import Response
from . serializers import *
from rest_framework.decorators import api_view,permission_classes, throttle_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from . models import *
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from django.conf import settings 
from django.middleware import csrf
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from . filters import *


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
        if serializer.context['authorization'] == 'Authorized':
            user = serializer.context['user']
            tokens = get_tokens_for_user(user)
            response = Response({"data":serializer.validated_data,"access_token":tokens['access']},status=status.HTTP_200_OK)

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=tokens["refresh"],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            )

            # setting the csrf token cookie
            csrf_token = csrf.get_token(request)
            response.set_cookie('csrftoken', csrf_token, samesite='Lax')

            return response
        
        else:
            return Response(status = status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    refresh_token = request.COOKIES.get('refresh_token')

    if refresh_token:
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        except Exception as e:
            return Response({"error":"There was an error invalidating the token:" + str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
    response = Response(status = status.HTTP_200_OK)
    response.delete_cookie("refresh_token")
    return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"errors":"Refresh token not provided"}, status = status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            data = {
                "access_token":access_token,
                "expiration_time":settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            }

            return Response({"token_data":data},status = status.HTTP_200_OK)

        except InvalidToken:
            return Response({"errors":"Invalid Token"},status = status.HTTP_401_UNAUTHORIZED)
        

@api_view('GET','POST')
def TransactionsList(request):
    pass 


@api_view(['GET','PUT','PATCH'])
def TransactionsDetail(request,pk):
    pass


@api_view(['POST'])
def VerifyMail(request):
    if request.method == 'POST':
        value = request.data.get('id')
        if not value:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            return Response(status = status.HTTP_404_NOT_FOUND)
        
        if user:
            user.verfied = True
            user.save()
            return Response(status = status.HTTP_200_OK)
        
    

@api_view(['POST'])
def create_tenant(request):
    if not request.user.approved or not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN)

    else:
        serializer = TenantCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        else:
            return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)