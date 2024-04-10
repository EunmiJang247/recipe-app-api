from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
) # url에 파라미터 담아서 필터링할때 씀

from rest_framework import (viewsets, mixins, status,) #  Django REST Framework에서 viewsets 모듈을 가져옴
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication # REST 프레임워크에서 토큰 인증을 사용하기 위해
from rest_framework.permissions import IsAuthenticated # 인증된 사용자인지 확인하기 위해
from core.models import (Recipe, Tag, Ingredient) # core 애플리케이션의 Recipe 모델을 가져옴
from recipe import serializers # recipe 애플리케이션의 serializers 모듈을 가져옴


@extend_schema_view( #필터링 기능을 위해 추가됨 API 뷰의 OpenAPI 스펙을 확장한다
    # API의 리스트 메서드에 필터링 기능을 추가하고, 해당 기능을 설명하기 위해 OpenAPI 스펙을 확장
    list=extend_schema( # list 메서드를 대상으로 스펙을 확장
        # tags 및 ingredients라는 두 개의 매개변수를 사용하여 필터링 기능을 제공
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR, # OpenAPI 스펙에서 사용되는 데이터 타입 = String
                description='Comma separed list of IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separed list of ingredient IDs to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """레시피 뷰셋"""
    '''
    viewsets.ModelViewSet 클래스를 상속받아서 만들어짐.
    이 클래스는 모델에 기반한 CRUD(Create, Retrieve, Update, Delete) 뷰를 제공함
    '''
    serializer_class = serializers.RecipeDetailSerializer # 사용할 직렬화 클래스를 지정
    queryset = Recipe.objects.all() # 모든 레시피 객체를 가져오는 쿼리셋
    authentication_classes = [TokenAuthentication]
    # 해당 뷰셋에 대한 사용자 인증 방식을 설정합니다. 여기서는 토큰 인증 방식을 사용
    permission_classes = [IsAuthenticated]
    #해당 뷰셋에 대한 사용자 권한을 설정합니다. 여기서는 인증된 사용자만 접근할 수 있도록 설정

    # 필터 구현
    def _params_to_ints(self, qs):
        # 쉼표로 구분된 각 값들을 정수로 변환하여 리스트로 반환하는 역할
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """인증된 사용자의 레시피만 반환"""
        # return self.queryset.filter(user=self.request.user).order_by('-id') 
        # 필터를 위한 기존라인 삭제
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # 테그 id 들이 배열형태로 담겨있음.
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            # 재료 id 들이 배열형태로 담겨있음.
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(user=self.request.user).order_by('-id').distinct() 
    #distinct() : 두번의 filter에서 동일한 결과가 나올수있으므로 고유값만 나오게 하려고

    
    def get_serializer_class(self):
        '''
        아래 코드를 통해 list 액션에 대한 직렬화 클래스를 
        RecipeSerializer로 설정하고, 나머지 액션에 대해서는 
        기본적으로 serializer_class(RecipeDetailSerializer)속성에서
        설정한 값을 사용합니다. 
        이는 API의 요청에 따라 서로 다른 직렬화 클래스를 사용할 수 있도록 합니다.
        '''
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """새로운 레시피 생성"""
        serializer.save(user=self.request.user)

    # 이미지 생성 뷰
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """이미지 업로드하는 뷰"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        # http://localhost:8000/static/media/uploads/recipe/d17dfbf4-43a1-47b1-8ee6-2269d9158744.png
        # 이주소를 반환해주는데 들어가면 볼수있음

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only', 
                #assigned_only로검색하면 레시피에 할당된 테그나 재료만 나오게됨
                OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, # 이거 넣었다고 patch가됨
                 mixins.DestroyModelMixin, # 이거 넣었다고 delete가됨
                 mixins.ListModelMixin, 
                 viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self): # get_queryset 메서드를 정의하고 있음
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
            # http://localhost:8000/api/recipe/ingredients/?assigned_only=1
            # 이런식으로 오면 assigned_only변수가 true가됨.
        ) 
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
          



