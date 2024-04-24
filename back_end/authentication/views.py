from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer # serialize User model to JSON
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userInfo(request):

    serializer = UserSerializer(request.user)

    return Response({
        json.dumps({
            "username": serializer.data["name"],
            "email": serializer.data["email"],
        }, cls=DjangoJSONEncoder)
    })
    