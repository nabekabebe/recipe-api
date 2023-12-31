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
GET_ME_URL = reverse('user:me')

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

    def test_get_user_unauthorized(self):
        """ Test that authentication is required to get user detial """

        res = self.client.get(GET_ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Test API requests that require authentication """

    def setUp(self):
        self.user = create_user(**USER_CREATE_PAYLOAD)
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        """ Test returns user profile for authenticated user """

        res = self.client.get(GET_ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_method_not_allowed(self):
        """ Test that POST method is not allowed on the me url """
        resp = self.client.post(GET_ME_URL, {})

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating user profile for authenticated user """
        update_payload = {'name': 'new Name', 'password': 'newpass123'}
        res = self.client.patch(GET_ME_URL, update_payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, update_payload['name'])
        self.assertTrue(self.user.check_password(update_payload['password']))


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
