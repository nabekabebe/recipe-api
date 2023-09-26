"""
Test for tag api
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


def get_tag_detial_url(tag_id):
    """Create and return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, name='Main Course'):
    """ Create and return a tag """
    return Tag.objects.create(user=user, name=name)


class PublicTagApiTests(TestCase):
    """ Test for unauthenticated users """

    def setUp(self):
        self.client = APIClient()

    def test_get_tag_for_unauthenticated_user_error(self):
        """ Test that tags cannot be retrieved by unauthenticated user """

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """ Test for authenticated api users"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_get_tags(self):
        """ Test retrieving tags """
        create_tag(self.user)
        create_tag(self.user, name='Vegan')

        resp = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), len(serializer.data))

    def test_get_tags_per_user(self):
        """ Test retrieving tags that belong to logged in user """
        otherUser = create_user(email='other@example.com')

        create_tag(user=otherUser)
        create_tag(user=self.user, name='some tag')

        resp = self.client.get(TAG_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), len(serializer.data))

    def test_update_tag_successful(self):
        """Test updating a tag"""

        tag = create_tag(user=self.user)
        payload = {'name': 'Updated Tag'}
        resp = self.client.put(get_tag_detial_url(tag.id), payload)

        tag.refresh_from_db()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(str(tag), payload['name'])

    def test_delete_tag_successful(self):
        """Test deleting a tag"""

        tag = create_tag(user=self.user)
        resp = self.client.delete(get_tag_detial_url(tag.id))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_delete_other_user_tag_error(self):
        """Test deleting other user's tag should error"""
        otherUser = create_user(email='other@example.com')
        tag = create_tag(user=otherUser)

        resp = self.client.delete(get_tag_detial_url(tag.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # def test_get_other_user_tag_successful(self):
        """ Test retriveing other users tag is possible"""

        """TODO: tags should be shared by all users
            -tags should only be deleted by admin
            -tags should not be case sensetive
        """
