from drf_spectacular.utils import (
	extend_schema_view,
	extend_schema,
	OpenApiParameter,
	OpenApiTypes,
)
'''
extend_schema_view: DRF 뷰셋에서 각 액션(method)에 대한 스키마 확장을 제공하는 데 사용됩니다. 
각 액션에 대한 개별 extend_schema 데코레이터를 적용할 수 있습니다

extend_schema: 특정 뷰 또는 뷰셋의 액션에 대해 OpenAPI 스키마를 확장하는 데 사용됩니다.
다양한 매개변수(예: 설명, 요청 및 응답 예시, 매개변수 등)를 제공하여 스키마를 커스터마이징할 수 있습니다

OpenApiParameter는 OpenAPI: 스펙에서 사용할 수 있는 매개변수를 정의하는 데 사용됩니다.
쿼리 파라미터, 경로 파라미터, 헤더 등 다양한 매개변수를 정의할 수 있습니다

OpenApiTypes는 OpenAPI: 스펙에서 사용할 수 있는 데이터 타입을 정의하는 클래스입니다.
문자열, 정수, 부울, 배열 등 다양한 데이터 타입을 제공합니다
'''

from rest_framework import (viewsets, mixins, status,) # Django REST Framework에서 viewsets 모듈을 가져옴
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication # REST 프레임워크에서 토큰 인증을 사용하기 위해
from rest_framework.permissions import IsAuthenticated # 인증된 사용자인지 확인하기 위해
from core.models import (Recipe, Tag, Ingredient) # core 애플리케이션의 Recipe 모델을 가져옴
from recipe import serializers # recipe 애플리케이션의 serializers 모듈을 가져옴

@extend_schema_view(
# @extend_schema_view는 Django REST Framework 뷰셋의 각 액션에 대해 OpenAPI 스키마를 확장할 수 있는 데코레이터
	list=extend_schema(
	# list 액션에 대한 추가적인 스키마 정보를 정의
		parameters=[
		# parameters는 API 엔드포인트가 받을 수 있는 쿼리 파라미터를 정의하는 데 사용됩니다. 
		# 여기서는 두 가지 쿼리 파라미터인 tags와 ingredients를 정의하고 있습니다
			OpenApiParameter(
			#  OpenAPI 스펙에서 사용할 수 있는 매개변수를 정의합니다. 여기서는 쿼리 파라미터를 정의하고 있습니다
				'tags', # 파라미터의 이름
				OpenApiTypes.STR, #파라미터의 데이터 타입
				description='Comma separed list of IDs to filter' #파라미터에 대한 설명입니다. 
				# 여기서는 필터링에 사용할 ID 목록을 콤마로 구분하여 전달할 수 있다고 설명하고 있습니다
			),
			OpenApiParameter(
			#  OpenAPI 스펙에서 사용할 수 있는 매개변수를 정의합니다. 여기서는 쿼리 파라미터를 정의하고 있습니다
				'ingredients', # 파라미터의 이름
				OpenApiTypes.STR, #파라미터의 데이터 타입
				description='Comma separed list of ingredient IDs to filter' #파라미터에 대한 설명입니다. 
			)
		]
	)
)

class RecipeViewSet(viewsets.ModelViewSet):
	"""레시피 뷰셋"""
	'''
	viewsets.ModelViewSet은 Django REST Framework에서 제공하는 클래스입니다. 
	이 클래스는 모델에 대해 표준 CRUD 작업을 수행할 수 있는 뷰셋을 만듭니다
	이 클래스는 모델에 기반한 CRUD(list, Create, Retrieve, Update, partial_update, Delete) 뷰를 제공함
	'''
	serializer_class = serializers.RecipeDetailSerializer
	queryset = Recipe.objects.all() # Recipe 모델의 모든 객체를 쿼리셋으로 반환합니다
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	# 필터 구현
	def _params_to_ints(self, qs):
		'''
			쿼리 파라미터로 전달된 문자열을 정수 목록으로 변환합니다
			qs: 쿼리 문자열입니다. 예: "1,2,3"
			반환값: 정수로 변환된 ID 목록입니다. 예: [1, 2, 3]
		'''
		return [int(str_id) for str_id in qs.split(',')]

	def get_queryset(self):
		# get_queryset 메서드는 Django REST Framework에서 GET 요청으로 목록을 조회할 때 사용되는 메서드입니다
		tags = self.request.query_params.get('tags')
		ingredients = self.request.query_params.get('ingredients')
		# url: http://localhost:90/api/recipe/recipes/?ingredients=바나나&tags=맛점
		'''
		쿼리 파라미터를 사용하여 필터링된 쿼리셋을 반환하는 과정을 설명합니다.
		이 메서드는 클라이언트가 제공한 쿼리 파라미터(tags 및 ingredients)를
		사용하여 Recipe 객체를 필터링하고, 최종적으로 현재 인증된 사용자의 필터링된 레시피 목록을 반환합니다
		'''
		queryset = self.queryset
		if tags:
			tag_ids = self._params_to_ints(tags)
			queryset = queryset.filter(tags__id__in=tag_ids)
			'''
			tag_ids = [1, 2, 3]인 경우, recipe의 tags 필드에서 
			id가 1, 2, 3 중 하나인 태그를 가진 레시피를 필터링합니다
			'''
		if ingredients:
			ingredient_ids = self._params_to_ints(ingredients)
			queryset = queryset.filter(ingredients__id__in=ingredient_ids)
		return queryset.filter(user=self.request.user).order_by('-id').distinct()
		# .distinct() : 중복방지	 

	
	def get_serializer_class(self):
		'''
		아래 코드를 통해 list 액션에 대한 직렬화 클래스를 
		RecipeSerializer로 설정하고, 
		나머지 액션에 대해서는 기본적으로 serializers.RecipeDetailSerializer속성에서
		설정한 값을 사용합니다. 이는 API의 요청에 따라 서로 다른 직렬화 클래스를 사용할 수 있도록 합니다.
		'''
		if self.action == 'list':
			return serializers.RecipeSerializer
		elif self.action == 'upload_image':
			return serializers.RecipeImageSerializer
		
		return self.serializer_class
	
	def perform_create(self, serializer):
		"""
		perform_create 메서드는 새로운 객체를 생성할 때 호출됩니다. 
		여기서 self는 뷰셋 인스턴스를 가리키고, serializer는 직렬화된 데이터를 가리킵니다.

		serializer.save(user=self.request.user)는 직렬화된 데이터를 데이터베이스에 
		저장하는 과정에서 현재 요청을 보낸 사용자를 user 필드에 추가합니다
		"""
		serializer.save(user=self.request.user)

	# 이미지 생성 뷰
	@action(methods=['POST'], detail=True, url_path='upload-image')
	# url이 /api/recipe/recipes/{id}/upload-image/가 됨. 
	# @action 데코레이터는 특정 HTTP 메서드(여기서는 POST)와 URL 경로(여기서는 'upload-image')에 매핑된 사용자 정의 액션을 만듭니다. 
	# 이 경우, 'upload-image'라는 경로로 POST 요청이 올 때 실행될 액션을 정의하고 있습니다
	#  detail=True로 설정되어 있어서 개별 객체(레시피에 사진 하나만 존재)에 대한 작업을 수행하는 것으로 추측됩니다
	def upload_image(self, request, pk=None):
		"""이미지 업로드하는 뷰"""
		# self는 ViewSet의 인스턴스를 참조합니다.
		recipe = self.get_object()
		# 메서드를 호출하여 현재 요청과 관련된 객체를 가져옵니다
		serializer = self.get_serializer(recipe, data=request.data)
		# recipe는 직렬화할 객체
		# data=request.data: 업로드된 이미지 데이터

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		# http://localhost:8000/static/media/uploads/recipe/d17dfbf4-43a1-47b1-8ee6-2269d9158744.png
		# 이주소를 반환해주는데 들어가면 볼수있음

@extend_schema_view(
# Django REST Framework에서 생성된 OpenAPI 스키마를 확장하거나 수정하기 위한 데코레이터
	list=extend_schema(
	# list 엔드포인트에 대한 스키마를 확장
		parameters=[
			OpenApiParameter(
				'assigned_only', # assigned_only라는 추가 매개변수를 정의
				OpenApiTypes.INT, enum=[0,1],
				#  레시피에 할당된 태그나 재료만 반환하도록 필터링 로직을 구현
				description='Filter by items assigned to recipes.',
			)
		]
	)
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, # PATCH 요청을 통해 모델 인스턴스를 업데이트할 수 있습니다
				 mixins.DestroyModelMixin, # DELETE 요청을 통해 모델 인스턴스를 삭제할 수 있습니다
				 mixins.ListModelMixin, # GET 요청을 통해 모델 인스턴스의 목록을 조회할 수 있습니다
				 viewsets.GenericViewSet): # 양한 CRUD 작업을 지원합니다
	authentication_classes = [TokenAuthentication]
	# 클라이언트는 요청 헤더에 유효한 토큰을 포함하여 인증을 수행해야 합니다
	permission_classes = [IsAuthenticated]
	# 인증된 사용자만 이 뷰셋에 접근할 수 있도록 제한합니다
	
	def get_queryset(self):
		'''
		queryset을 가져올 때 특정 조건에 따라 필터링된 결과를 반환하는 역할을 합니다.
		주로 사용자가 요청한 매개변수에 따라 queryset을 동적으로 변경할 때 사용됩니다
		'''
		assigned_only = bool(
			int(self.request.query_params.get('assigned_only', 0))
		)
		'''
		이 부분은 URL 쿼리 매개변수에서 assigned_only라는 매개변수의 값을 가져옵니다.
		URL에 assigned_only 매개변수가 포함되지 않은 경우 기본값으로 0을 반환합니다.
		예를 들어, http://localhost:8000/api/recipe/ingredients/?assigned_only=1라고 하면 assigned_only의 값은 1이 됩니다.
		http://localhost:8000/api/recipe/ingredients/처럼 assigned_only 매개변수가 없으면 기본값 0이 사용됩니다.
		'''
		queryset = self.queryset
		if assigned_only:
			queryset = queryset.filter(recipe__isnull=False)
			# 레시피가 할당되어 있는 재료 또는 테그들만을 필터링하여 가져오도록 하는 것

		return queryset.filter(user=self.request.user).order_by('-name').distinct()
	

class TagViewSet(BaseRecipeAttrViewSet):
	""" DB의 테그를 관리 """
	serializer_class = serializers.TagSerializer
	queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
	serializer_class = serializers.IngredientSerializer
	queryset = Ingredient.objects.all()
		  



