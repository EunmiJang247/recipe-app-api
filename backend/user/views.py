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
	# ObtainAuthToken은 Django REST Framework에서 제공하는 기본 클래스이며, 사용자 인증 토큰을 생성하는 기능을 제공
	serializer_class = AuthTokenSerializer
	renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
	'''
	Django REST Framework에서 API 응답을 렌더링할 때 사용할 렌더러 클래스를 지정하는 설정입니다. 
	이 설정은 뷰 또는 뷰셋의 응답 형식을 정의하는 데 사용됩니다.
	이를 통해 JSON, HTML, XML 등의 형식으로 API 응답을 렌더링할 수 있습니다
	'''

class ManageUserView(generics.RetrieveUpdateAPIView):
	"""
	ManageUserView 클래스는 Django REST Framework를 사용하여 사용자의 정보를 조회하고 업데이트하는 API 뷰
	RetrieveUpdateAPIView를 상속받아 사용자의 세부 정보를 가져오고 업데이트하는 기능을 제공함
	"""
	serializer_class = UserSerializer
	authentication_classes = [authentication.TokenAuthentication]
	# TokenAuthentication은 토큰 기반 인증 방식을 사용합니다. 클라이언트는 요청 헤더에 Token을 포함하여 인증을 수행해야 합니다
	# 사용자가 누구인지를 확인
	permission_classes = [permissions.IsAuthenticated]
	# IsAuthenticated는 사용자가 인증된 경우에만 이 뷰에 접근할 수 있도록 제한합니다. 인증되지 않은 사용자는 이 뷰에 접근할 수 없습니다
	# 사용자가 접근할 수 있는 권한이 있는지를 확인

	def get_object(self):
		# get_object 메서드는 현재 요청을 보낸 인증된 사용자 객체를 반환합니다
		"""get_object는 Django REST Framework에서 제공하는 제네릭 뷰 클래스의 메서드 중 하나입니다. 
		이 메서드는 특정 객체를 가져오거나 조회하는 데 사용됩니다. 
		제네릭 뷰 클래스에서 객체를 검색하고 반환하는 기본 동작을 정의합니다.
		이 메서드는 주어진 조건에 맞는 객체를 검색하고 반환하는 데 사용됩니다
		"""
		return self.request.user
	