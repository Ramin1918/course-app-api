"""
Tests for models.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from course import models
from django.core.files.uploadedfile import SimpleUploadedFile


def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_kurs(self):
        """Test creating a kurs is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        kurs = models.Kurs.objects.create(
            user=user,
            author='Sample author name',
            title='Sample course name',
            price=Decimal('5.50'),
            description='Sample course description.',
        )

        self.assertEqual(str(kurs), kurs.title)

    # def test_create_material(self):
    #     """Test creating a material is successful."""
    #     user = create_user()
    #     material = models.Material.objects.create(user=user, name='Material1')

    #     self.assertEqual(str(material), material.name)
    def test_create_material(self):
        """Test creating a material is successful."""
        user = create_user()

        # Create a sample video file for testing
        video_content = b"Sample video content"
        video = SimpleUploadedFile("video.mp4", video_content, content_type="video/mp4")
        material = models.Material.objects.create(user=user, name='Material1', video=video)

        self.assertEqual(str(material), material.name)
        self.assertIsNotNone(material.video)
        self.assertTrue(material.video.name.startswith("course_videos/"))
        with material.video.open() as file:
            self.assertEqual(file.read(), video_content)
