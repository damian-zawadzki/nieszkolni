from django.test import RequestFactory, TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from nieszkolni_app.models import *

from .views import *


class YourTestClass(TestCase):
    def setUp(self):
        global userfullname
        global username
        global password

        userfullname = "Joe Doe"
        username = "joedoe"
        password = "1234"
        self.user = User.objects.create_user(username, 'joedoe@dummy.com', password)

    def test_campus_deny_anonymous(self):
        response = self.client.get('/campus', follow=True)
        self.assertRedirects(response, '/login_user?next=/campus')

    # def test_flashcard(self):
    #     global userfullname
    #     global username
    #     global password
    #     self.client.login(username="joedoe", password="1234")

    #     klient = Client()
    #     self.klient = Client.objects.create(name="Joe Doe")

    #     userfullname1 = "Damien%20Bunny"
    #     url = reverse("flashcard", kwargs={"username":userfullname1, "deck":"vocabulary"})

    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'flashcard.html')

    # def test_call_view_load(self):
    #     self.client.login(username='joedoe', password='1234')
    #     response = self.client.get('/campus')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'campus.html')

    # def test_random_test(self):
    #     self.client.login(username='joedoe', password='1234')
    #     response = self.client.get('/applause/1')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'applause.html')