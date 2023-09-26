from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
# from django.db.utils import IntegrityError

from core import models


def create_user(email='test@example.com', password='testpass123'):
    """ Create and return a user """
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """ Testing the models """

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """

        email = 'email@exampl.com'
        password = 'testpass123'
        user = create_user(email=email, password=password)

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

        for email, normalized_email in sample_emails:
            user = create_user(email=email)
            self.assertEqual(user.email, normalized_email)

    def test_new_user_without_email_raises_error(self):
        """ Test creating user without email raises error """

        with self.assertRaises(ValueError):
            create_user(email=None)

    def test_create_super_user(self):
        """ Test creating a new super user """

        user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_successful(self):
        """ Testing creating a recipe """

        user = create_user()

        recipe = models.Recipe.objects.create(
            user=user,
            title='Recipe Title',
            time_minutes=5,
            price=Decimal('10.00'),
            description='Simple recipe description'
        )

        self.assertEqual(str(recipe), 'Recipe Title')

    def test_create_tag_successful(self):
        """ Test creating a new tag """

        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Vegan')

        self.assertEqual(str(tag), 'Vegan')

    # def test_create_tag_with_existing_name_error(self):
    #     """Test creating a tag with existing name raises error"""

    #     user = create_user()

    #     models.Tag.objects.create(user=user, name='Vegan')

    #     with self.assertRaises(IntegrityError):
    #         models.Tag.objects.create(user=user, name='Vegan')

    def test_create_ingredient_successful(self):
        """Test create an ingredient"""
        user = create_user()
        models.Ingredient.objects.create(
            user=user,
            name='Lettuce'
        )

        self.assertTrue(
            models.Ingredient.objects.filter(
                user=user, name='Lettuce').exists())
