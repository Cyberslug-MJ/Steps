from .models import CustomUser as User 
from django.db.models.signals import post_save
from . models import *
from django.dispatch import receiver
import string
import secrets


@receiver(post_save, sender=User)
def CreateProfile(sender,created,instance,**kwargs):
    if created:
        UserProfile.objects.create(
            user = instance,
            firstname = instance.first_name,
            lastname = instance.last_name,
            email = instance.email
        )

    else:
        updated = False
        if instance.profile.firstname != instance.first_name:
            instance.profile.firstname = instance.first_name
            updated = True
        
        if instance.profile.lastname != instance.last_name:
            instance.profile.lastname = instance.last_name
            updated = True
        
        if instance.profile.email != instance.email:
            instance.profile.email = instance.email
            updated = True

        if updated:
            instance.profile.save()


@receiver(post_save,sender=User)
def CreateSchoolProfile(sender,created,instance,**kwargs):
    if created:
        if instance.role == "Admin":
            SchoolProfile.objects.create(
                user = instance
            )


@receiver(post_save,sender=User)
def Creator(sender,created,instance,**kwargs):
    if created:
        if instance.role == "Parent":
            Parents.objects.create(
                user = instance
            )
        
        if instance.role == "Student":
            passkey = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            Student.objects.create(
                user = instance,
                my_passkey = passkey
            )
        
        if instance.role=="Teacher":
            Staff.objects.create(
                user=instance,
            )
            
            if instance.approved == False:
                Approvals.objects.create(
                    user=instance,
                    firstname = instance.staff.firstname,
                    lastname = instance.staff.lastname,
                    email = instance.email,
                    approved = instance.approved
                )
            