from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    """ Testing the models """

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """

        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email(self):
        """ Test the email for a new user is normalized """

        sample_emails = [
            ('Test@example.com', 'Test@example.com'),
            ('TEST@EXAMPLE.com', 'TEST@example.com'),
            ('TEst@example.com', 'TEst@example.com'),
            ('test@EXAMPLE.COM', 'test@example.com')
        ]

        password = 'testpass123'

        for email, normalized_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password=password
            )
            self.assertEqual(user.email, normalized_email)

    def test_new_user_without_email_raises_error(self):
        """ Test creating user without email raises error """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='testpass123'
            )

    def test_create_super_user(self):
        """ Test creating a new super user """

        email = 'admin@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_successful(self):
        """ Testing creating a recipe """

        email = 'admin@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Recipe Title',
            time_minutes=5,
            price=Decimal('10.00'),
            description='Simple recipe description'
        )

        self.assertEqual(str(recipe), 'Recipe Title')
