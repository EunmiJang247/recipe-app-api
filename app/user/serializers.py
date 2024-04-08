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
    # serializers.ModelSerializer를 상속

    class Meta:
        # Meta 클래스 내부에서는 해당 시리얼라이저가 어떤 모델을 기반으로 동작할지 설정합니다
        model = get_user_model()
        '''
        get_user_model() 함수는 Django의 django.contrib.auth 
        모듈에서 제공하는 get_user_model() 함수입니다.
        이 함수는 현재 프로젝트에서 사용 중인 사용자 
        모델을 반환합니다.
        '''
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

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
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        trim_whitespace=False
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
        return attrs