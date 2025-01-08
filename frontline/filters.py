from dataclasses import field
from sched import Event
import django
import django_filters
from backline.models import *
from django_filters import FilterSet


class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Events
        fields = ['event_tags','completed']


class AnnouncementFilter(FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    audiences = django_filters.CharFilter(lookup_expr='exact')
    class Meta:
        model = Announcements
        fields = ['title','audiences','priority']


class RecordFilter(FilterSet):
    student_firstname = django_filters.CharFilter(field_name='student__firstname',lookup_expr='icontains')
    subject_name = django_filters.CharFilter(field_name='subject__name',lookup_expr='icontains')
    academic_year_name = django_filters.CharFilter(field_name='academic_year__name',lookup_expr='icontains')
    total_score = django_filters.RangeFilter()
    class Meta:
        model = Assessment_records
        fields = ['student_firstname','subject_name','academic_year_name','total_score']


class ClassesFilter(FilterSet):
    class Meta:
        model = StudentClasses
        fields = ['name']


class SubClassFilter(FilterSet):
    Grade_name = django_filters.CharFilter(field_name='Grade__name',lookup_expr='icontains')
    supervisors_firstname = django_filters.CharFilter(field_name='supervisors__firstname',lookup_expr='icontains')
    class Meta:
        model = SubClasses
        fields = ['name','Grade_name','supervisors_firstname']


class AcademicFilter(FilterSet):
    class Meta:
        model = Academic
        fields = ['name','is_active']

    
class SubjectFilter(FilterSet):
    classes_name = django_filters.CharFilter(field_name='classes__name',lookup_expr='icontains')
    supervisors_firstname = django_filters.CharFilter(field_name='supervisors__firstname',lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Subjects
        fields = ['name','classes_name','supervisors_firstname']

    
class StudentFilter(FilterSet):
    fullname = django_filters.CharFilter(lookup_expr='icontains')
    student_class = django_filters.CharFilter(field_name='student_class__name',lookup_expr='icontains')
    class Meta:
        model = Student
        fields = ['fullname','student_class']


class StaffFilter(FilterSet):
    fullname = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Staff
        fields = ['fullname']


class ParentFilter(FilterSet):
    fullname = django_filters.CharFilter(lookup_expr='icontains')
    ward_name = django_filters.CharFilter(field_name='ward_name__firstname',lookup_expr='icontains')
    class Meta:
        model = Parents
        fields = ['fullname','ward_name']


class AttendanceFilter(FilterSet):
    student_name = django_filters.CharFilter(field_name='student__name',lookup_expr='icontains')
    academic_calendar = django_filters.CharFilter(field_name='academic_calendar__name',lookup_expr='icontains')
    class Meta:
        model = Attendance
        fields = ['status','date','academic_calendar','student_name']


class ApprovalsFilter(FilterSet):
    class Meta:
        model = Approvals 
        fields = ['approved','firstname','lastname','email']
