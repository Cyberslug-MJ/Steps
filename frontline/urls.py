from . import views 
from django.urls import path 

urlpatterns = [
    path('api/register',views.register,name='register'),
    path('api/login',views.login,name='login'),
    path('api/profile/<int:pk>/',views.ProfileManager,name='profile'),
    path('',views.home,name='home'),
    path('api/announcements',views.Announcement,name='api-announcements'),
    path('api/announcements/<int:pk>/',views.AnnouncementDetail,name='api-announcement-detail'),
    path('api/events',views.EventScheduler,name='events'),
    path('api/events/<int:pk>/',views.EventDetail,name='event-detail'),
    path('api/profiles',views.profiles,name='profiles'),
    path('api/school-profile/<int:pk>/',views.SchoolProfileManager,name='school-profile'),
    path('api/subclasses',views.SubClasses_me,name='subclasses'),
    path('api/logout',views.logout,name='logout'),
    path('api/student',views.StudentCreator,name='add_student'),
    path('api/student/<int:pk>/',views.StudentDetail,name='student-detail'),
    path('api/import-file',views.ImportExport,name='import-file'),
    path('api/import-students',views.ImportStudents,name='import-students'),
]