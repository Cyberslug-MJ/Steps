from .models import CustomUser
from django.db.models.signals import post_save
from . models import *
from django.dispatch import receiver


@receiver(post_save,sender=CustomUser)
def CreateProfile(sender,created,instance,**kwargs):
    if created:
        UserProfile.objects.create(
            user = instance,
            firstname = instance.first_name,
            lastname = instance.last_name,
            email = instance.email
        )
        #print('User Profile Created')

    else:
        updated = False
        if instance.profile.firstname != instance.firstname:
            instance.profile.firstname = instance.firstname
            updated = True
        
        if instance.profile.lastname != instance.lastname:
            instance.profile.lastname = instance.lastname
            updated = True
        
        if instance.profile.email != instance.email:
            instance.profile.email = instance.email
            updated = True

        if updated:
            instance.profile.save()
        #    print('User Profile Updated')