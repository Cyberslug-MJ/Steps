from django.contrib import admin
from . models import *
from . forms import CustomUserForm
from django.contrib.auth.admin import UserAdmin


registry = [UserProfile,Events,Announcements]
admin.site.register(registry)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserForm
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Roles',{'fields':('role',)}),
        ('School',{'fields':('school_name',)}),
        ('Approved',{'fields':('approved',)}),
    )

    # You can also customize the fields displayed in the add/edit form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role','school_name'),
        }),
    )



admin.site.register(CustomUser,CustomUserAdmin)