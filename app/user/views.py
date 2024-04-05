"""
유저 api의 뷰
"""

from rest_framework import generics
from user.serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
