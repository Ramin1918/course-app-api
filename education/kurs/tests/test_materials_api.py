from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

from course.models import Material
from kurs.serializers import MaterialSerializer

MATERIALS_URL = reverse('kurs:material-list')

def detail_url(material_id):
    """Create and return a material detail url."""
    return reverse('kurs:material-detail', args=[material_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PrivateMaterialsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_materials(self):
        """Test retrieving a list of materials."""
        # Create sample video files
        video_content_1 = b"Sample video content 1"
        video_content_2 = b"Sample video content 2"

        video_1 = SimpleUploadedFile("video1.mp4", video_content_1, content_type="video/mp4")
        video_2 = SimpleUploadedFile("video2.mp4", video_content_2, content_type="video/mp4")

        # Create materials with associated video files
        material1 = Material.objects.create(user=self.user, name='Vegan', video=video_1)
        material2 = Material.objects.create(user=self.user, name='Dessert', video=video_2)

        res = self.client.get(MATERIALS_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check if the video field is present in the response
        self.assertIn('video', res.data[0])

        # Check if the video file content matches the original content
        with material1.video.open() as file:
            self.assertEqual(file.read(), video_content_1)

        with material2.video.open() as file:
            self.assertEqual(file.read(), video_content_2)

    def test_materials_limited_to_user(self):
        """Test list of materials is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        video_content = b"Sample video content"
        video = SimpleUploadedFile("video.mp4", video_content, content_type="video/mp4")
        Material.objects.create(user=user2, name='Fruity', video=video)
        material = Material.objects.create(user=self.user, name='Comfort Food', video=video)

        res = self.client.get(MATERIALS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], material.name)
        self.assertEqual(res.data[0]['id'], material.id)

        # Check if the video field is present in the response
        self.assertIn('video', res.data[0])

        # Check if the video file content matches the original content
        with material.video.open() as file:
            self.assertEqual(file.read(), video_content)



    def test_update_material(self):
        """Test updating a material."""
        material = Material.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(material.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        material.refresh_from_db()
        self.assertEqual(material.name, payload['name'])

    def test_delete_material(self):
        """Test deleting a material."""
        material = Material.objects.create(user=self.user, name='Breakfast')


        url = detail_url(material.id)
        res = self.client.delete(url)


        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        materials = Material.objects.filter(user=self.user)
        self.assertFalse(materials.exists())




# """
# Tests for the tags API.
# """
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from django.test import TestCase

# from rest_framework import status
# from rest_framework.test import APIClient

# from course.models import Material

# from kurs.serializers import MaterialSerializer


# MATERIALS_URL = reverse('kurs:material-list')


# def create_user(email='user@example.com', password='testpass123'):
#     """Create and return a user."""
#     return get_user_model().objects.create_user(email=email, password=password)


# class PublicMaterialsApiTests(TestCase):
#     """Test unauthenticated API requests."""

#     def setUp(self):
#         self.client = APIClient()

#     def test_auth_required(self):
#         """Test auth is required for retrieving materials."""
#         res = self.client.get(MATERIALS_URL)

#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateMaterialsApiTests(TestCase):
#     """Test authenticated API requests."""

#     def setUp(self):
#         self.user = create_user()
#         self.client = APIClient()
#         self.client.force_authenticate(self.user)

#     def test_retrieve_materials(self):
#         """Test retrieving a list of materials."""
#         Material.objects.create(user=self.user, name='Vegan')
#         Material.objects.create(user=self.user, name='Dessert')

#         res = self.client.get(MATERIALS_URL)

#         materials = Material.objects.all().order_by('-name')
#         serializer = MaterialSerializer(materials, many=True)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def test_materials_limited_to_user(self):
#         """Test list of materials is limited to authenticated user."""
#         user2 = create_user(email='user2@example.com')
#         Material.objects.create(user=user2, name='Fruity')
#         material = Material.objects.create(user=self.user, name='Comfort Food')

#         res = self.client.get(MATERIALS_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), 1)
#         self.assertEqual(res.data[0]['name'], material.name)
#         self.assertEqual(res.data[0]['id'], material.id)


