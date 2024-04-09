from rest_framework import (viewsets, mixins, status,) #  Django REST Framework에서 viewsets 모듈을 가져옴
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication # REST 프레임워크에서 토큰 인증을 사용하기 위해
from rest_framework.permissions import IsAuthenticated # 인증된 사용자인지 확인하기 위해
from core.models import (Recipe, Tag, Ingredient) # core 애플리케이션의 Recipe 모델을 가져옴
from recipe import serializers # recipe 애플리케이션의 serializers 모듈을 가져옴

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

    def get_queryset(self):
        """인증된 사용자의 레시피만 반환"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
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
        """이미지 업로드하는 부분"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, # 이거 넣었다고 patch가됨
                 mixins.DestroyModelMixin, # 이거 넣었다고 delete가됨
                 mixins.ListModelMixin, 
                 viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')
        #이 줄 때문에 로그인한 사람의 재료만 볼수있는것임.  
    

class TagViewSet(BaseRecipeAttrViewSet):
    """ DB의 테그를 관리 """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
          



