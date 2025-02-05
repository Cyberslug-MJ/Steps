from . import views 
from django.urls import path 
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/add-user',views.UserList,name='add-user'),
    path('api/edit-user/<int:pk>/',views.UserDetail,name='edit-user'),
    path('api/school-detail',views.SchoolDetail,name='school-detail'),
    path('api/confirm_mail',views.ChangeMail,name='change-mail'),
    path('api/approvals',views.ApprovalsList,name='approvals-list'),
    path('api/approvals/<int:pk>/',views.ApprovalsDetail,name='approvals-detail'),
    path('api/profile',views.ProfileManager,name='profile'),
    path('api/announcements',views.AnnouncementList,name='announcements'),
    path('api/announcements/<int:pk>/',views.AnnouncementDetail,name='announcement-detail'),
    path('api/events',views.EventList,name='events'),
    path('api/events/<int:pk>/',views.EventDetail,name='event-detail'),
    path('api/profiles',views.profiles,name='profiles'),
    path('api/school-profile/<int:pk>/',views.SchoolProfileManager,name='school-profile'),
    path('api/subclasses',views.SubClassesList,name='subclasses'),
    path('api/subclasses/<int:pk>/',views.SubclassesDetail,name='subclasses-detail'),
    path('api/students',views.StudentList,name='add_student'),
    path('api/students/<int:pk>/',views.StudentDetail,name='student-detail'),
    path('api/classes',views.ClassesList,name='classes-List'),
    path('api/classes/<int:pk>/',views.ClassesDetail,name='classes-detail'),
    path('api/academic',views.AcademicList,name='academic-List'),
    path('api/academic/<int:pk>/',views.AcademicDetail,name='academic-detail'),
    path('api/subjects',views.SubjectsList,name='subjects-manager'),
    path('api/subjects/<int:pk>/',views.SubjectDetail,name='subjects-detail'),
    path('api/staff',views.StaffList,name='staff-List'),
    path('api/staff/<int:pk>/',views.StaffDetail,name='staff-detail'),
    path('api/parents',views.ParentList,name='parent-list'),
    path('api/parents/<int:pk>/',views.ParentDetail,name='parent-detail'),
    path('api/add-ward/<int:pk>/',views.add_ward,name='add-ward'),
    path('api/records',views.RecordList,name='record-list'),
    path('api/records/<int:pk>/',views.RecordDetail,name='record-detail'),
    path('api/import-file',views.ImportExport,name='import-file'),
    path('api/import-students',views.ImportStudents,name='import-students'),
]