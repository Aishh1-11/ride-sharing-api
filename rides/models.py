from django.db import models
from django.contrib.auth.models import User


class RidesModel(models.Model):

    STATUS_CHOICES = [
        ("requested","Requested"),
        ("accepted","Accepted"),
        ("started", "Started"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled") 
    ]

    rider = models.ForeignKey(User,on_delete=models.CASCADE,related_name="rides_requested")
    driver = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="rides_driven")

    pickup_location = models.CharField(max_length=100)
    dropoff_location = models.CharField(max_length=100)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="requested")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    current_location = models.CharField(max_length=100,null=True,blank=True)

    
class Profile(models.Model):
    ROLE_CHOICES = [
        ("rider", "Rider"),
        ("driver", "Driver")
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
