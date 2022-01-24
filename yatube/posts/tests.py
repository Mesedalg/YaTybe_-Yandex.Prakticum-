from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.core.cache import cache

import tempfile
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow


TEST_CACHE_SETTING = {}


class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="12345"
        )
        self.post = Post.objects.create(text="Random clever text", author=self.user)

    def test_profile(self):
        response_profile = self.client.get("/testuser/")
        self.assertEqual(response_profile.status_code, 200)
        self.assertEqual(len(response_profile.context["page"]), 1)
        self.assertEqual(response_profile.context["page"][0].text, "Random clever text")
        self.assertIsInstance(response_profile.context["user"], User)
        self.assertEqual(response_profile.context["user"].username, self.user.username)

    def test_posts_appears(self):
        cache.clear()
        response_index = self.client.get("")
        self.assertEqual(response_index.context["page"][0].text, "Random clever text")
        response_new_page = self.client.get(f"/{self.user.username}/{self.post.pk}/")
        self.assertEqual(response_new_page.context["post"].text, "Random clever text")

    def test_login_post_creation_and_commenting(self):
        self.client.login(username="testuser", password="12345")
        response_creation_access_login = self.client.get("/new/")
        self.assertEqual(response_creation_access_login.status_code, 200)
        response_comment = self.client.post(f"/{self.user.username}/{self.post.pk}/comment", {'author':self.user, 'text': 'Test text', 'post': self.post})
        self.assertEqual(response_comment.status_code, 302)
        self.assertRedirects(response_comment, f"/{self.user.username}/{self.post.pk}/")

    def test_logiout_post_creation_and_commenting(self):
        response_creation_access_logout = self.client.get("/new/")
        self.assertRedirects(response_creation_access_logout, '/auth/login/?next=/new/')
        response_comment = self.client.post(f"/{self.user.username}/{self.post.pk}/comment", {'author':self.user, 'text': 'Test text', 'post': self.post})
        self.assertEqual(response_comment.status_code, 302)
        self.assertRedirects(response_comment, f"/auth/login/?next=/{self.user.username}/{self.post.pk}/comment")


    def test_post_editing(self):
        self.post.text = f"TestEdit: {self.post.text}"
        self.post.save()
        response_profile = self.client.get("/testuser/")
        cache.clear()
        response_index = self.client.get("")
        response_new_page = self.client.get(f"/{self.user.username}/{self.post.pk}/")
        self.assertEqual(response_new_page.context["post"].text, "TestEdit: Random clever text")
        self.assertEqual(response_index.context["page"][0].text, "TestEdit: Random clever text")
        self.assertEqual(response_profile.context["page"][0].text, "TestEdit: Random clever text")
        form = PostForm()
        self.assertTrue(form.fields)


class NewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_new_post(self):
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 302)


class ErrorTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_error(self):
        response = self.client.get("hiseg5f54n")
        self.assertEqual(response.status_code, 404)


class ImageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="12345"
        )
        self.image = tempfile.NamedTemporaryFile(suffix=".jpg", dir="").name
        self.group = Group.objects.create(title="Test title", slug="testgroupf", description="Test description")
        self.post = Post.objects.create(text="Random clever text", image=self.image, author=self.user, group=self.group)

    def test_image_on_pages(self):
        response_new_page = self.client.get(f"/{self.user.username}/{self.post.pk}/")
        self.assertContains(response_new_page, '<img')
        self.assertEqual(response_new_page.context["post"].image, self.image)
        response_index = self.client.get("")
        self.assertContains(response_index, '<img')
        response_profile = self.client.get(f"/{self.user.username}/")
        self.assertEqual(response_profile.status_code, 200)
        self.assertContains(response_profile, '<img')
        response_group = self.client.get(f"/group/{self.group.slug}")
        self.assertEqual(response_group.status_code, 200)
        self.assertContains(response_group, '<img')

    def test_non_image_upload(self):
        with open('posts/tests.py', 'rb') as txt:
            post = self.client.post(f"{self.user.username}/{self.post.pk}/edit/",
                                    {'author': self.user, 'text': 'post with image', 'image': txt})
            self.assertEqual(post.status_code, 404)


class FollowingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="12345"
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="12345"
        )
        self.image = tempfile.NamedTemporaryFile(suffix=".jpg", dir="").name
        self.group = Group.objects.create(title="Test title", slug="testgroupf", description="Test description")
        self.post = Post.objects.create(text="Random clever text", image=self.image, author=self.user, group=self.group)

    def test_follow_posts_unfollow_with_login(self):
        self.client.login(username="testuser", password="12345")
        url = reverse('profile_follow', args=["testuser2"])
        response_following = self.client.get(url)
        self.assertRedirects(response_following, '/testuser2/')
        author = get_object_or_404(User, username="testuser2")
        user = get_object_or_404(User, username="testuser")
        following = Follow.objects.get(user=user, author=author)
        self.assertEqual(str(following), 'testuser2 followed by testuser')
        self.post = Post.objects.create(text="Random clever text2", image=self.image, author=self.user2, group=self.group)
        response_follow_posts = self.client.get(f"/follow/")
        self.assertEqual(response_follow_posts.context["page"][0].text, "Random clever text2")
        url = reverse('profile_unfollow', args=["testuser2"])
        response_unfollowing = self.client.get(url)
        self.assertRedirects(response_unfollowing, '/testuser2/')
        author = get_object_or_404(User, username="testuser2")
        user = get_object_or_404(User, username="testuser")
        following = Follow.objects.filter(user=user, author=author)
        self.assertEqual(str(following), '<QuerySet []>')

    def test_follow_without_login(self):
        url = reverse('profile_follow', args=["testuser2"])
        response_following = self.client.get(url)
        self.assertRedirects(response_following, '/auth/login/?next=/testuser2/follow/')

    def test_show_post_in_follow_page_without_login(self):
        self.client.login(username="testuser2", password="12345")
        response_follow_posts = self.client.get(f"/follow/")
        posts_len = len(response_follow_posts.context["page"])
        self.post = Post.objects.create(text="Random clever text2", image=self.image, author=self.user, group=self.group)
        response_follow_posts2 = self.client.get(f"/follow/")
        self.assertEqual(len(response_follow_posts2.context["page"]), posts_len)



