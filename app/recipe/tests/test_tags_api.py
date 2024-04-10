"""
테그 테스트를 위한 api 테스트
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Tag, Recipe)
from recipe.serializers import (
    TagSerializer,
)

TAGS_URL = reverse('recipe:tag-list') 
# reverse 함수는 Django의 URL 리버스(Reverse) 기능을 사용하여 URL을 생성하는 함수.

# detail tag를 위해 아래를 추가함.
def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@exmaple.com', password="testpass123"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """로그인 안한사람들 request"""
    
    def setUp(self):
        # setUp 메서드에서는 각 테스트 메서드가 실행되기 전에 self.client를 초기화
        self.client = APIClient()
        #  Django REST Framework의 테스트 유틸리티 중 하나로, 테스트 케이스에서 API를 호출하는 데 사용됨

    def test_auth_required(self):
        # 로그인하지 않은 사용자의 GET 요청이 401 Unauthorized 상태 코드를 반환하는지 확인
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ 로그인한 사람들 테스트"""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        # 테스트 시에 임의의 사용자를 인증 상태로 만들어주는 역할

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        # Tag.objects.create() 메서드를 사용하여 테스트 코드에서 새로운 Tag 객체를 데이터베이스에 생성

        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        # 생성한 테그가 모두 잘 있는지 확인

    def test_tags_limited_to_user(self):
        # 내가 생성한 테그만 나오는지 확인
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        # print(self.user) # user@exmaple.com

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # print(tag.name) #Comfort Food
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)


    # 테그 수정하는 기능 테스트
    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])


    # 삭제 기능 테스트
    def test_delete_tag(self):
        """ Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())


    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        # tag2는 할당되지 않았는데 그거 잘걸려내는지 확인

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """필터 결과가 중복된거 주지않는지 검사"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pencakes',
            time_minutes=5,
            price=Decimal('5.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        # Dinner은 할당되지 않았는데 그게맞는지 검사
        self.assertEqual(len(res.data), 1)

