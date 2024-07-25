""" 
데이터베이스 모델. 
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
	AbstractBaseUser,
	BaseUserManager,
	PermissionsMixin,
)

def recipe_image_file_path(instance, filename):
	"""generate file path for new recipe image"""
	ext = os.path.splitext(filename)[1]
	filename = f'{uuid.uuid4()}{ext}'

	return os.path.join('static', 'recipe', filename)


# 유저 모델을 만들었으니 유저모델 매니저를 만들어보겠다 
class UserManager(BaseUserManager): 
	#BaseUserManager : 장고에 의해 구현되어있는 것
	#사용자 모델을 커스터마이징할 때 사용자 생성과 관련된 기본 기능을 제공하기 위해 상속받음. 
	def create_user(self, email, password=None, **extra_fields):
		""" 유저생성 """
		if not email:
			raise ValueError('User must have an email address.')
		user = self.model(email=self.normalize_email(email), **extra_fields)
		# self.model을 사용하여 새로운 User 인스턴스를 생성
		# 제공된 이메일 주소를 표준화(소문자로 변환 등)하여 email 필드에 할당
		# **extra_fields는 추가로 제공된 키워드 인자들을 모두 받아서 모델 인스턴스 생성 시 함께 전달합니다
		user.set_password(password) # 비밀번호 암호화 및 설정
		user.save(using=self._db) # 데이터베이스에 저장

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
	# AbstractBaseUser: Django의 기본 사용자 모델. 사용자 인증을 위한 기본 필드(password, last_login 등)와 메서드(set_password(), check_password() 등)를 제공
	# is_superuser 필드는 PermissionsMixin 클래스에서 제공됩니다.

	# PermissionsMixin: Django의 권한 및 그룹 관리를 위한 믹스인 클래스. 사용자의 권한을 관리하기 위한 필드(is_superuser, groups, user_permissions)와 메서드(has_perm(), has_module_perms() 등)를 제공
	# 별도로 password 필드를 모델에 정의하지 않아도 AbstractBaseUser를 상속받으면 자동으로 해당 필드를 사용할 수 있습니다

	email = models.EmailField(max_length=255, unique=True) # 이메일 필드 정의
	name = models.CharField(max_length=255) # 네임 필드 정의 
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	# 이거 선언 시 이메일, 이름, 활성화여부, 스태프인지여부를 넣었음. 

	objects = UserManager() 
	# UserManager 사용할 수 있도록 활성화.
	# Django 모델에서 커스텀 매니저를 사용하기 위해 지정하는 것
	# 기본 UserManager를 재정의하여 사용자 생성 시 추가적인 로직을 포함할 수 있습니다.
	# 예를 들어, 이메일을 필수로 하고, 비밀번호를 암호화하는 등의 로직을 추가할 수 있습니다

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
	price = models.DecimalField(max_digits=8, decimal_places=2)
	link = models.CharField(max_length=255, blank=True)
	tags = models.ManyToManyField('Tag')
	ingredients = models.ManyToManyField('Ingredient')
	image = models.ImageField(null=True, upload_to=recipe_image_file_path)

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
		settings.AUTH_USER_MODEL, # settings.py에 AUTH_USER_MODEL = 'core.User' 코어모델쓰겠다는뜻
		on_delete=models.CASCADE,
	)

	def __str__(self):
		return self.name 
	#str(ingredient(Ingredient인스턴스))찍으면 name이 대표로 나옴



