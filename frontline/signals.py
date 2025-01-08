from .models import CustomUser as User 
from django.db.models.signals import post_save
from . models import *
from django.dispatch import receiver


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