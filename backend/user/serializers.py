"""
API뷰 시리얼라이저
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,   
)

from django.utils.translation import gettext as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    # ModelSerializer: 모델의 필드를 자동으로 직렬화하고 역직렬화하는 기능을 제공

    class Meta: #Meta: 직렬화할 모델과 필드 목록이 포함됨
        model = get_user_model()
        '''
        get_user_model() 함수는 Django의 django.contrib.auth 
        모듈에서 제공하는 get_user_model() 함수입니다.
        이 함수는 현재 프로젝트에서 사용 중인 사용자 모델을 반환합니다.
        '''
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        '''
        write_only=True: 이 필드는 쓰기 작업(예: 객체 생성 또는 업데이트)에서만 사용되고, 
        읽기 작업(예: 객체 조회)에서는 제외됩니다. 즉, JSON 응답에는 포함되지 않습니다
        '''

    def create(self, validated_data):
        # post요청을 보내면 이게 호출됨
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
        # ** : 딕셔너리를 함수의 인자로 전달할 수 있도록 해줌.
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
    
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField() # 유효한 이메일 형식인지 확인
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        trim_whitespace=True
    )

    def validate(self, attrs):
        """유저 벨리데이팅"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        # attrs['user'] = user: 인증에 성공한 경우, attrs 사전에 user 객체를 추가합니다
        return attrs