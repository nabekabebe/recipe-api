"""
Test for recipe API
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer, RecipeDetailSerializer
)


RECIPE_URL = reverse('recipe:recipe-list')

RECIPE_PAYLOAD = {
        'title': 'Sample Recipe',
        'description': 'Sample Description',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'link': 'http://exmple.com/recipe.pdf'
    }


def recipe_detail_url(recipe_id):
    """ Return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **data):
    """ Create and return recipe """

    RECIPE_PAYLOAD.update(data)

    return Recipe.objects.create(user=user, **RECIPE_PAYLOAD)


def create_user(**data):
    """Create and return a user"""
    return get_user_model().objects.create_user(**data)


class PublicRecipeApiTests(TestCase):
    """Test for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_recipe_get_error_for_unauthenticated_user(self):
        """ Test recipes cannot be retrieved by unauthenticated user """

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """ Test authenticated recipe API access """

    def setUp(self):
        self.user = create_user(
            email='recipe@example.com',
            password='testpass123'
            )
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_recipe_get_all_recipes(self):
        """Test getting all recipes for authenticated user"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_get_per_user(self):
        """Testing getting recipes that belong to loggedin user"""
        otherUser = create_user(
            email='other@example.com',
            password='testpass123'
        )
        create_recipe(user=otherUser)
        create_recipe(user=self.user)

        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), len(serializer.data))

    def test_recipe_detail_view(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)

        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_create(self):
        """Test create a recipe test"""

        resp = self.client.post(RECIPE_URL, RECIPE_PAYLOAD)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=resp.data['id'])

        # Check if the recipe is created with the correct data
        for key, value in RECIPE_PAYLOAD.items():
            self.assertEqual(value, getattr(recipe, key, None))

        # Check if the recipe is created for the loggedin user
        self.assertEqual(recipe.user, self.user)

    def test_recipe_partial_update(self):
        """Test updating a recipe with patch"""
        recipe = create_recipe(user=self.user)
        payload = {'title': 'New Title'}
        resp = self.client.patch(recipe_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.description, RECIPE_PAYLOAD['description'])

    def test_recipe_full_update(self):
        """Test updating a recipe with put"""

        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'New Title',
            'description': 'New Description',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'link': 'http://exmple.com/new_recipe.pdf'
        }
        resp = self.client.put(recipe_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check if the recipe is created with the correct data
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key, None))

    def test_get_other_user_recipe_error(self):
        """Test that cuurent user cannot view other user recipe"""

        otherUser = create_user(
            email='other@example.com',
            password='testpass123')
        recipe = create_recipe(user=otherUser)

        resp = self.client.get(recipe_detail_url(recipe.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recipe_success(self):
        """Test deleting a recipe"""

        recipe = create_recipe(user=self.user)

        resp = self.client.delete(recipe_detail_url(recipe.id))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_update_recipe_owner_should_not_work(self):
        """Test updating user through recipe should not work"""

        otherUser = create_user(
            email='other@example.com',
            password='testpass123')

        recipe = create_recipe(user=self.user)

        self.client.patch(
            recipe_detail_url(recipe.id),
            {'user': otherUser.id}
        )
        recipe.refresh_from_db()
        self.assertNotEqual(recipe.user.id, otherUser.id)

    def test_create_recipe_with_new_tags_successful(self):
        """ Test creating a new recipe with new tags successful """
        payload = {}
        payload.update(RECIPE_PAYLOAD)
        payload['tags'] = [
            {'name': 'Tag 1'},
            {'name': 'Tag 2'}
        ]

        resp = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        tags = Tag.objects.filter(user=self.user)

        self.assertEqual(tags.count(), recipe.tags.count())
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            tag_exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(tag_exists)

    def test_create_recipe_with_existing_tags(self):
        """ Test creating a new recipe with existing tags should override"""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        payload = {}
        payload.update(RECIPE_PAYLOAD)
        payload['tags'] = [
            {'name': 'Vegan'},
            {'name': 'Dinner'},
        ]

        resp = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())

        for tag in payload['tags']:
            tag_exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(tag_exists)

    def test_create_tag_on_recipe_update(self):
        """ Test creating a tag on recipe update"""

        payload = {
            'tags': [{'name': 'Lunch'}]
        }

        recipe = create_recipe(user=self.user)

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            payload,
            format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 1)
        tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """ Test updating a recipe with tags should replace recipe tags"""

        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)

        payload = {
            'tags': [
                {'name': 'new tag'}
            ]
        }

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            payload,
            format='json')

        newtag = Tag.objects.get(user=self.user, name='new tag')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertNotIn(tag1, recipe.tags.all())
        self.assertIn(newtag, recipe.tags.all())

    def test_clear_recipe_tags_with_empty_update(self):
        """ Test clear recipe tags with empty tags array update"""
        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            {'tags': []},
            format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_ingredients_successful(self):
        """ Test creating a new recipe with new ingredients successful """
        payload = {}
        payload.update(RECIPE_PAYLOAD)
        payload['ingredients'] = [
            {'name': 'Lettuce'},
            {'name': 'Tomato'},
        ]

        resp = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(len(recipes), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            self.assertTrue(
                Ingredient.objects.filter(user=self.user, **ingredient))

    def test_create_ingredient_on_recipe_update(self):
        """ Test creating a ingredient on recipe update"""

        payload = {
            'ingredients': [{'name': 'Lettuce'}]
        }

        recipe = create_recipe(user=self.user)

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            payload,
            format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 1)
        ingredient = Ingredient.objects.get(user=self.user, name='Lettuce')
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test updating recipe with ingredients replaces recipe ingredients"""

        ingredient1 = Ingredient.objects.create(
            user=self.user, name='ingredient 1')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        payload = {
            'ingredients': [
                {'name': 'new ingredient'}
            ]
        }

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            payload,
            format='json')

        newingredient = Ingredient.objects.get(
            user=self.user, name='new ingredient')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertNotIn(ingredient1, recipe.ingredients.all())
        self.assertIn(newingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients_with_empty_update(self):
        """ Test clear recipe ingredients with empty ingredients update"""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='ingredient 1')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        resp = self.client.patch(
            recipe_detail_url(recipe.id),
            {'ingredients': []},
            format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
