from django.contrib import admin
from .models import *


registry = [Events,Announcements,Parents,SubClasses,Staff,Student,StudentClasses,Attendance,Academic,Subjects,Assessment_records,Approvals]
admin.site.register(registry)