from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):

    role = serializers.ChoiceField(choices=["rider", "driver"], write_only=True)

    class Meta:
        model = User
        fields = ["id","username","password","role"]
        extra_kwargs ={
            "password":{"write_only":True}
        }

    def create(self,validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, role=role)
        return user
    

class RidesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RidesModel
        fields = "__all__"
        read_only_fields = ['rider','driver','status','created_at','updated_at',"current_location"]
