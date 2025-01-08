from .models import CustomUser as User 
from django.db.models.signals import post_save
from . models import *
from django.dispatch import receiver
import string
import secrets

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
    

    else:

        if instance.role == "Student":
            instance.student.firstname = instance.first_name
            instance.student.lastname = instance.last_name 
            instance.student.student_class = instance.student.student_class
            instance.student.save()


        if instance.role == "Parent":
            instance.parent.firstname = instance.first_name 
            instance.parent.lastname = instance.last_name
            instance.parent.wards.set(instance.parent.wards.all()) # add new wards or just update the old ones
            instance.parent.save()


        if instance.role == "Teacher":
            instance.staff.firstname = instance.first_name 
            instance.staff.lastname = instance.last_name
            instance.staff.save()