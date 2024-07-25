"""
유저 api의 뷰
"""

from rest_framework import generics, authentication, permissions
# Django REST Framework에서 제공하는 기능들을 사용하기위함

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

class CreateUserView(generics.CreateAPIView):
    # CreateUserView는 새로운 사용자를 생성하는 API 엔드포인트를 제공
    # POST 요청을 처리하여 새로운 객체를 생성하는 기능을 제공
    serializer_class = UserSerializer
    # UserSerializer는 사용자 데이터를 검증하고, 새로운 사용자 객체를 생성하는 역할

class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer # 아이디로 이메일을 사용하기 위해 선언
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
    