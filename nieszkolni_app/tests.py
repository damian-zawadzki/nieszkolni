from django.test import RequestFactory, TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from nieszkolni_app.models import *

from .views import *


class Front(TestCase):
    def setUp(self):
        global username
        global password
        global current_user
        global current_client

        username = "joedoe"
        password = "1234"
        first_name = "Joe"
        last_name = "Doe"
        current_user = first_name + " " + last_name
        current_client = "Damian Bunny"

        self.user = User.objects.create_user(
                username,
                'joedoe@dummy.com',
                password,
                first_name=first_name,
                last_name=last_name
                )

        self.user.save()

        self.user_2 = User.objects.create_user(
                "damianbunny",
                "damianbunny@dummy.com",
                "1234",
                first_name="Damian",
                last_name="Bunny"
                )

        self.user_2.save()

        self.coach = Client.objects.create(name="Joe Doe")

    def test_campus_deny_anonymous(self):
        response = self.client.get("/campus/", follow=True)
        self.assertRedirects(response, "/login_user/?next=/campus/")

    def test_campus_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/campus/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "campus.html")

    def test_challenges_deny_anonymous(self):
        response = self.client.get("/challenges/")
        self.assertRedirects(response, "/login_user/?next=/challenges/")

    def test_challenges_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/challenges/")
        self.assertEqual(response.status_code, 302)

    def test_profile_deny_anonymous(self):
        response = self.client.get("/profile/")
        self.assertRedirects(response, "/login_user/?next=/profile/")

    def test_profile_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_ranking_deny_anonymous(self):
        response = self.client.get("/ranking/")
        self.assertRedirects(response, "/login_user/?next=/ranking/")

    def test_ranking_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/ranking/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ranking.html")

    def test_coach_deny_anonymous(self):
        response = self.client.get("/coach/")
        self.assertRedirects(response, "/admin/login/?next=/coach/")

    def test_coach_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/coach/")
        self.assertEqual(response.status_code, 302)

    def test_coach_login_staff(self):
        Card.objects.create(client=current_client)
        Client.objects.create(name=current_client)
        CurrentClient.objects.create(
            coach=current_user,
            name=current_client
            )

        self.client.login(username=username, password=password)
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse("coach"))
        self.assertEqual(response.status_code, 200)

    def test_staff_deny_anonymous(self):
        response = self.client.get("/staff/")
        self.assertRedirects(response, "/admin/login/?next=/staff/")

    def test_staff_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/staff/")
        self.assertEqual(response.status_code, 302)

    def test_staff_login_staff(self):
        self.client.login(username=username, password=password)
        self.user.is_staff = True
        self.user.save()
        response = self.client.get("/staff/")
        self.assertEqual(response.status_code, 200)

    def test_assignments_deny_anonymous(self):
        response = self.client.get("/assignments/")
        self.assertRedirects(response, "/login_user/?next=/assignments/")

    def test_assignments_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assignments.html")

    def test_my_statistics_deny_anonymous(self):
        response = self.client.get("/my_statistics/")
        self.assertRedirects(response, "/login_user/?next=/my_statistics/")

    def test_my_statistics_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/my_statistics/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_statistics.html")

    def test_memories_deny_anonymous(self):
        response = self.client.get("/memories/")
        self.assertRedirects(response, "/login_user/?next=/memories/")

    def test_memories_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/memories/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "memories.html")

    def test_list_of_submissions_deny_anonymous(self):
        response = self.client.get("/list_of_submissions/")
        self.assertRedirects(response, "/login_user/?next=/list_of_submissions/")

    def test_list_of_submissions_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/list_of_submissions/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list_of_submissions.html")

    def test_options_deny_anonymous(self):
        response = self.client.get("/options/")
        self.assertRedirects(response, "/login_user/?next=/options/")

    def test_options_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/options/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "options.html")

    def test_vocabulary_deny_anonymous(self):
        response = self.client.get("/vocabulary/")
        self.assertRedirects(response, "/login_user/?next=/vocabulary/")

    def test_vocabulary_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/vocabulary/")
        self.assertEqual(response.status_code, 302)

    def test_sentences_deny_anonymous(self):
        response = self.client.get("/sentences/")
        self.assertRedirects(response, "/login_user/?next=/sentences/")

    def test_sentences_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/sentences/")
        self.assertEqual(response.status_code, 302)

    def test_pronunciation_deny_anonymous(self):
        response = self.client.get("/my_pronunciation/")
        self.assertRedirects(response, "/login_user/?next=/my_pronunciation/")

    def test_pronunciation_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/my_pronunciation/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_pronunciation.html")

    def test_flashcard_deny_anonymous(self):
        url = reverse("flashcard", args=["Joe Doe", "vocabulary"])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login_user.html")

    def test_flashcard_login_no_object(self):
        self.client.login(username=username, password=password)
        url = reverse("flashcard", args=["Joe Doe", "vocabulary"])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "congratulations.html")

    def test_flashcard_login(self):
        self.client.login(username=username, password=password)
        Card.objects.create(client=current_user)
        url = reverse("flashcard", args=["Joe Doe", "vocabulary"])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "congratulations.html")

    def test_my_courses_deny_anonymous(self):
        response = self.client.get("/my_courses/")
        self.assertRedirects(response, "/login_user/?next=/my_courses/")

    def test_my_courses_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/my_courses/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_courses.html")

    def test_my_result_deny_anonymous(self):
        response = self.client.get("/my_results/")
        self.assertRedirects(response, "/login_user/?next=/my_results/")

    def test_my_result_login(self):
        self.client.login(username=username, password=password)
        response = self.client.get("/my_results/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_results.html")


'''
vocabulary with flashcards in it
sentences with flashcards in it
detailed assignment views
'''
