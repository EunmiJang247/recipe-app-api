"""
유저 API테스트
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """ Create and retrun new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ 로그인이 불필요한 api테스트"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """유저생성이 성공적으로 되었는지 확인"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """ 유저가 존재하는지 확인!"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ 패스워드가 5글자이상인지 확인"""
        payload = {
            'email': 'test@example.com',
            'password': '122',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)