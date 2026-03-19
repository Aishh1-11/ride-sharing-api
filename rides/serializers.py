from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","username","password"]
        extra_kwargs ={
            "password":{"write_only":True}
        }

    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class RidesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RidesModel
        fields = "__all__"
        read_only_fields = ['rider','driver','status','created_at','updated_at',"current_location"]
