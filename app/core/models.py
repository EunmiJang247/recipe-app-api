""" 
데이터베이스 모델. 
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# 유저 모델을 만들었으니 유저모델 매니저를 만들어보겠다 
class UserManager(BaseUserManager): #BaseUserManager : 장고에 의해 구현되어있는 것
    """ 유저 관리 부분 """
    def create_user(self, email, password=None, **extra_fields):
        """ 유저생성 """
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password) #암호화된 암호를 저장
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        """ 슈퍼유저 생성"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# 모델 추가하겠다
class User(AbstractBaseUser, PermissionsMixin):
    # 필드를 정의하겠다
    # AbstractBaseUser : Auth기능을 가지고있음
    # PermissionsMixin : 허가해주는 기능을 가지고있음
    email = models.EmailField(max_length=255, unique=True) # 이메일 필드 정의
    name = models.CharField(max_length=255) # 네임 필드 정의 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() # UserManager 사용할 수 있도록 활성화.

    # 아이디를 email로 사용하게 해줌.
    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self):
        return self.title
    
class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        # settings.py에 AUTH_USER_MODEL = 'core.User' 코어모델쓰겠다는뜻
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name 
    #str(ingredient(Ingredient인스턴스))찍으면 name이 대표로 나옴



