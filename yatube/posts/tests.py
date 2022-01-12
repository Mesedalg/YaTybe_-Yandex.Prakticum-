from django.contrib.auth.models import User
from django.test import TestCase, Client

from .forms import PostForm
from .models import Post


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
        self.assertEqual(response_profile.status_code,200)
        self.assertEqual(len(response_profile.context["page"]), 1)
        self.assertEqual(response_profile.context["page"][0].text, "Random clever text")
        self.assertIsInstance(response_profile.context["user"], User)
        self.assertEqual(response_profile.context["user"].username, self.user.username)
        response_index = self.client.get("")
        self.assertEqual(response_index.context["page"][0].text, "Random clever text")
        response_new_page = self.client.get(f"/{self.user.username}/{self.post.pk}/")
        self.assertEqual(response_new_page.context["post"].text, "Random clever text")
        self.client.login(username="testuser", password="12345")
        response_creation_access_login = self.client.get("/new/")
        self.assertEqual(response_creation_access_login.status_code, 200)
        self.client.logout()
        response_creation_access_logout = self.client.get("/new/")
        self.assertEqual(response_creation_access_logout.status_code, 302)
        self.post.text = f"TestEdit: {self.post.text}"
        self.post.save()
        response_profile = self.client.get("/testuser/")
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

    def test_cteate_new_post(self):
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 302)
    def test_show_msg(self):
        self.assertTrue(True, msg="Важная проверка на истинность")