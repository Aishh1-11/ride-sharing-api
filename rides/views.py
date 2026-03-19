from rest_framework.views import APIView
from .serializers import *

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
import datetime,jwt
from django.conf import settings

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication

from rest_framework.decorators import action


class UserRegister(APIView):

    def post(self,request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,status.HTTP_201_CREATED)
    

    
class UserLogin(APIView):

    def post(self,request):

        username = request.data['username']
        password = request.data['password']

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
    def status(self, request, pk=None):

        ride = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = ["started", "completed", "cancelled"]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"})
        
        ride.status = new_status
        
        ride.save()
        return Response({"message": "status updated"})

    @action(detail=True, methods=['patch'])
    def accept_ride(self, request, pk=None):

        ride = self.get_object()
       
        
        if ride.status != "requested" :
            return Response({"message":"Request Already Accepted"},status=status.HTTP_400_BAD_REQUEST)    
        if ride.rider == request.user:
            return Response({"message":"Rider cannot be driver"},status=status.HTTP_400_BAD_REQUEST)
        
        ride.status = 'accepted'
        ride.driver = request.user
               

        ride.save()
        return Response({"message":"Ride accepted"})

            
    





        

  


