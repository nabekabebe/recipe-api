"""
Test user api endpoint
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN = reverse('user:token')

USER_CREATE_PAYLOAD = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test Name'
    }


def create_user(**params):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test the public users API """

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user_successful(self):
        """ Test creating user with valid payload is successful """

        res = self.client.post(CREATE_USER_URL, USER_CREATE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=USER_CREATE_PAYLOAD['email'])
        self.assertTrue(user.check_password(USER_CREATE_PAYLOAD['password']))
        self.assertNotIn('password', res.data)

    def test_existing_email_raises_error(self):
        """ Test creating user with existing email raises error """

        create_user(**USER_CREATE_PAYLOAD)

        res = self.client.post(CREATE_USER_URL, USER_CREATE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that password must be more than 8 characters """
        res = self.client.post(CREATE_USER_URL, {
            **USER_CREATE_PAYLOAD, 'password': 'pw'
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=USER_CREATE_PAYLOAD['email']).exists()
        self.assertFalse(user_exists)


class AuthTokenTests(TestCase):
    """ Test for user token generation """

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_existing_user(self):
        """ Generate token for user with valid credentials """

        create_user(**USER_CREATE_PAYLOAD)

        res = self.client.post(CREATE_TOKEN, USER_CREATE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_invalid_credentials_error(self):
        """ Test returns error for invalid credentials """
        create_user(**USER_CREATE_PAYLOAD)

        res = self.client.post(CREATE_TOKEN, {
            **USER_CREATE_PAYLOAD,
            'email': 'wrong@example.com',
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
