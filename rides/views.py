from rest_framework.views import APIView
from .serializers import *

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
import datetime,jwt
from django.conf import settings

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication

from rest_framework.decorators import action
from django.utils import timezone


class UserRegister(APIView):

    def post(self,request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,status.HTTP_201_CREATED)
    

    
class UserLogin(APIView):

    def post(self,request):

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username,password=password)
        if user is None:
            raise AuthenticationFailed("Invalid Credentials")
        
        now = datetime.datetime.utcnow()
        
        payload ={
            "id" : user.id,
            "exp" : now + datetime.timedelta(minutes=120),
            "iat" : now
        }

        token = jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
        response = Response({'message':"login Success"})
        response.set_cookie(key='jwt',value=token, httponly=True)


        return response
    


class JWTCookieAuthentication(BaseAuthentication):

    def authenticate(self,request):

        token = request.COOKIES.get('jwt')

        if not token :
            return None
        
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token Expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user,None)
        
        



    
class UserLogout(APIView):

    def post(self,request):

        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message":"logout"}

        return response


    

class RidesView(viewsets.ModelViewSet):
     
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = RidesSerializer
    model = RidesModel
    queryset = RidesModel.objects.all()

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)



    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):

        ride = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = ["started", "completed", "cancelled"]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"})
        
        ride.status = new_status

        if new_status == "started":
            ride.current_location = ride.pickup_location
        if new_status == "completed":
            ride.current_location = ride.dropoff_location
        
        ride.save()
        return Response({"message": "status updated"})
    


    @action(detail=True, methods=['patch'])
    def accept_ride(self, request, pk=None):

        ride = self.get_object()
       
        if request.user.profile.role != "driver":
            return Response({"error": "Only drivers can accept rides"}, status=status.HTTP_400_BAD_REQUEST)
        if ride.status != "requested" :
            return Response({"message":"Request Already Accepted"},status=status.HTTP_400_BAD_REQUEST)    
        if ride.rider == request.user:
            return Response({"message":"Rider cannot be driver"},status=status.HTTP_400_BAD_REQUEST)
        
        
        ride.status = 'accepted'
        ride.driver = request.user
               

        ride.save()
        return Response({"message":"Ride accepted"},status=status.HTTP_200_OK)
    

    
    @action(detail=True, methods=['patch'])
    def update_current_location(self, request, pk = None):

        ride = self.get_object()
        location = request.data.get('current_location')

        if ride.driver != request.user:
            return Response({"message":"Only driver can update current location"},status=status.HTTP_400_BAD_REQUEST)
        
        if ride.status != "started":
            return Response({"message":"Ride is not active, Cannot update current location"},status=status.HTTP_400_BAD_REQUEST)
        
        ride.current_location = location
        ride.save()
        return Response({"message":"Location updated successfully"},status=status.HTTP_200_OK)
    


    @action(detail=False, methods=["get"])
    def match_driver(self,request):

        ride = RidesModel.objects.filter(
            rider=request.user,
            status="requested"
            ).first()
         
        if not ride:
            return Response({"error": "No active ride request found"}, status=404)

        pickup_location = ride.pickup_location

        busy_drivers = RidesModel.objects.filter(status__in = ["accepted","started"]).values_list("driver",flat=True)

        recent_time = timezone.now() - datetime.timedelta(minutes=20)

        available_drivers = User.objects.filter(profile__role="driver").exclude(id__in = busy_drivers).exclude(id=request.user.id)
        nearby_rides = RidesModel.objects.filter(driver__in = available_drivers, current_location = pickup_location, updated_at__gte = recent_time).order_by('-updated_at')
        
        result = []
        nearby_driver_ids = []

        if nearby_rides.exists():
            
            for r in nearby_rides:
                result.append({
                    "driver":r.driver.username,
                    "current_location":r.current_location,
                    "last_active":r.updated_at
                })

            nearby_driver_ids = nearby_rides.values_list('driver', flat=True)
        

        for driver in available_drivers.exclude(id__in=nearby_driver_ids):
            result.append({
                "driver": driver.username,
                "current_location": "unknown",
                "last_active": "unknown"
                })
            
        if result:
            return Response(result)
        
        return Response({"message": "No drivers available"}, status=status.HTTP_404_NOT_FOUND)

    
        


    


    
     



            
    





        

  


