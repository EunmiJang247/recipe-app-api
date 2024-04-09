"""
Ingredient 테스트를 위한 api 테스트
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import (
    IngredientSerializer,
)

INGREDIENTS_URL = reverse('recipe:ingredient-list') 

# detail ingredient를 위해 아래를 추가함.
def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@exmaple.com', password="testpass123"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """로그인 안한사람들 request"""
    
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """ 로그인한 사람들 테스트"""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Fruity')
        
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL) #로그인한 유저의 모든 재료를 get
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)


    # 재료 수정하는 기능 테스트
    def test_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        # 재료생성

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        # Coriander를 보냄

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db() # db새로고침
        self.assertEqual(ingredient.name, payload['name'])


    # 재료 삭제 테스트
    # def test_delete_ingredient(self):
    #     ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

    #     url = detail_url(ingredient.id)
    #     res = self.client.delete(url)

    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    #     ingredient = Ingredient.objects.filter(user=self.user)
    #     self.assertFalse(ingredient.exists())

