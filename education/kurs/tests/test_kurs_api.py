"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from course.models import Kurs

from kurs.serializers import KursSerializer, KursDetailSerializer


KURSES_URl = reverse('kurs:kurs-list')


def detail_url(kurs_id):
    """Create and return a kurs detail URL."""
    return reverse('kurs:kurs-detail', args=[kurs_id])


def create_kurs(user, **params):
    """Create and return a sample kurs."""
    defaults = {
        'author': 'Sample author name',
        'title': 'Sample kurs title',
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/kurs.pdf',
    }
    defaults.update(params)

    kurs = Kurs.objects.create(user=user, **defaults)
    return kurs

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicKursAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(KURSES_URl)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateKursApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_kurses(self):
        """Test retrieving a list of kurses."""
        create_kurs(user=self.user)
        create_kurs(user=self.user)

        res = self.client.get(KURSES_URl)

        kurses = Kurs.objects.all().order_by('-id')
        serializer = KursSerializer(kurses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_kurs_list_limited_to_user(self):
        """Test list of kurses is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        create_kurs(user=other_user)
        create_kurs(user=self.user)

        res = self.client.get(KURSES_URl)

        kurses = Kurs.objects.filter(user=self.user)
        serializer = KursSerializer(kurses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_kurs_detail(self):
        """Test get kurs detail."""
        kurs = create_kurs(user=self.user)

        url = detail_url(kurs.id)
        res = self.client.get(url)

        serializer = KursDetailSerializer(kurs)
        self.assertEqual(res.data, serializer.data)

    def test_create_kurs(self):
        """Test creating a kurs."""
        payload = {
            'title': 'Sample kurs',
            'author': 'Sample author',
            'price': Decimal('5.99'),
        }
        res = self.client.post(KURSES_URl, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        kurs = Kurs.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(kurs, k), v)
        self.assertEqual(kurs.user, self.user)

    def test_partial_update(self):
        """Test partial update of a kurs."""
        original_link = 'https://example.com/kurs.pdf'
        kurs = create_kurs(
            user=self.user,
            title='Sample kurs title',
            link=original_link,
        )

        payload = {'title': 'New kurs title'}
        url = detail_url(kurs.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        kurs.refresh_from_db()
        self.assertEqual(kurs.title, payload['title'])
        self.assertEqual(kurs.link, original_link)
        self.assertEqual(kurs.user, self.user)

    def test_full_update(self):
        """Test full update of kurs."""
        kurs = create_kurs(
            user=self.user,
            title='Sample kurs title',
            link='https://exmaple.com/kurs.pdf',
            description='Sample kurs description.',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'author': 'Sample author name',
            'price': Decimal('2.50'),
        }
        url = detail_url(kurs.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        kurs.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(kurs, k), v)
        self.assertEqual(kurs.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the kurs user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        kurs = create_kurs(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(kurs.id)
        self.client.patch(url, payload)

        kurs.refresh_from_db()
        self.assertEqual(kurs.user, self.user)

    def test_delete_kurs(self):
        """Test deleting a kurs successful."""
        kurs = create_kurs(user=self.user)

        url = detail_url(kurs.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Kurs.objects.filter(id=kurs.id).exists())

    def test_kurs_other_users_kurs_error(self):
        """Test trying to delete another users kurs gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        kurs = create_kurs(user=new_user)

        url = detail_url(kurs.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Kurs.objects.filter(id=kurs.id).exists())
