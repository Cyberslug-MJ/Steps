from . import views 
from django.urls import path 

urlpatterns = [
    path('api/register',views.register,name='register'),
    path('api/login',views.login,name='login'),
    path('api/profile',views.ProfileManager,name='profile'),
    path('',views.home,name='home'),
    path('api/announcements',views.Announcement,name='api-announcements'),
    path('api/announcements/<int:pk>/',views.AnnouncementDetail,name='api-announcement-detail'),
    path('api/events',views.EventScheduler,name='events'),
    path('api/events/<int:pk>/',views.EventDetail,name='event-detail'),    
]