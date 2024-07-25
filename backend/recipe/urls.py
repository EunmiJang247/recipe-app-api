from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()

router.register('recipes', views.RecipeViewSet) 
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe' # URL 패턴을 구별하기 위해 사용 

urlpatterns = [
    path('', include(router.urls))
]