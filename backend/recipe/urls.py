from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter() #  뷰셋(ViewSet)을 기반으로 자동으로 URL을 생성
router.register('recipes', views.RecipeViewSet) 
# router 변수를 사용하여 'recipes'라는 경로에 대한 URL 패턴을 RecipeViewSet 뷰셋(ViewSet)에 등록

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)


app_name = 'recipe' # URL 패턴을 구별하기 위해 사용 

urlpatterns = [
    path('', include(router.urls))
]