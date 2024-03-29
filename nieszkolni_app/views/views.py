from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.db import transaction
from django.db import IntegrityError
from django.db import connection

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings as django_settings
from django.core.files.base import ContentFile, File
from django_user_agents.utils import get_user_agent
from django.template import RequestContext

from nieszkolni_app.models import *

from nieszkolni_folder.vocabulary_manager import VocabularyManager
from nieszkolni_folder.clients_manager import ClientsManager
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.submission_manager import SubmissionManager
from nieszkolni_folder.string_to_csv import StringToCsv
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.current_clients_manager import CurrentClientsManager
from nieszkolni_folder.knowledge_manager import KnowledgeManager
from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.cleaner import Cleaner
from nieszkolni_folder.wordcounter import Wordcounter
from nieszkolni_folder.sentence_manager import SentenceManager
from nieszkolni_folder.back_office_manager import BackOfficeManager
from nieszkolni_folder.document_manager import DocumentManager
from nieszkolni_folder.roadmap_manager import RoadmapManager
from nieszkolni_folder.download_manager import DownloadManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.curriculum_planner import CurriculumPlanner
from nieszkolni_folder.homework_manager import HomeworkManager
from nieszkolni_folder.activity_manager import ActivityManager
from nieszkolni_folder.rating_manager import RatingManager
from nieszkolni_folder.audit_manager import AuditManager
from nieszkolni_folder.onboarding_manager import OnboardingManager
from nieszkolni_folder.back_office_planner import BackOfficePlanner
from nieszkolni_folder.challenge_manager import ChallengeManager
from nieszkolni_folder.survey_manager import SurveyManager
from nieszkolni_folder.analytics_manager import AnalyticsManager
from nieszkolni_folder.translation_manager import TranslationManager
from nieszkolni_folder.dna_manager import DnaManager
from nieszkolni_folder.speech_manager import SpeechManager
from nieszkolni_folder.product_manager import ProductManager

from io import BytesIO

import csv
import re
import json
import os
import requests
import random
import plotly.express as px
import pandas as pd

from .staff_views import *
from .views import *


def get_current_user(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return current_user

    else:
        return None


def view_404(request, exception=None):
    return redirect("/")


def welcome(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        total_phrases = VocabularyManager().total_cards(current_user)
        new_phrases = VocabularyManager().new_cards(current_user, "vocabulary")

        return redirect("campus")

    else:

        if request.method == "POST":
            return redirect("login_user")
        else:
            return render(request, 'welcome.html', {})


@login_required
def campus(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        announcements = BackOfficeManager().display_latest_announcements_for_client(current_user)
        announcements = TimeMachine().convert_to_date_time_clean(announcements, 1)

        challenges = ChallengeManager().display_planned_challenges(current_user)
        challenge_status = ChallengeManager().refresh_process(challenges)

        score = ActivityManager().calculate_points_this_week(current_user)
        ratings = RatingManager().display_unrated(current_user)

        overdue_assignments = CurriculumManager().display_overdue_assignments(current_user)
        uncompleted_assignments = CurriculumManager().display_uncompleted_assignments(current_user)
        completed_assignments = CurriculumManager().display_completed_assignments(current_user)

        last_week_points = ActivityManager().get_homework_points_last_week(
                current_user
                )

        lightbox = StreamManager().check_sensor_today_for_client(
                current_user,
                "lightbox"
                )
        conditions = ActivityManager().check_conditions_last_week(current_user)

        user_agent = get_user_agent(request)

        if request.method == "POST":
            if request.POST["action_on_campus"] == "lightbox":
                StreamManager().add_to_stream(
                        current_user,
                        "Sensor",
                        "lightbox",
                        current_user
                        )

                return redirect("campus")

        context = {
            "overdue_assignments": overdue_assignments,
            "uncompleted_assignments": uncompleted_assignments,
            "completed_assignments": completed_assignments,
            "score": score,
            "ratings": ratings,
            "announcements": announcements,
            "last_week_points": last_week_points,
            "lightbox": lightbox,
            "conditions": conditions
            }

        if not challenge_status:
            return redirect("challenges")

        if user_agent.is_mobile:
            return render(request, 'm_campus.html', context)
        else:
            return render(request, 'campus.html', context)


@staff_member_required
def lightbox_results(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        QuizManager().download_graded_quizzes()

        context = {}

        return render(
            request,
            "lightbox_results.html",
            context
            )


@login_required
def office(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, 'm_office.html', {
                "announcements": announcements
                })
        else:
            return render(request, 'office.html', {
                "announcements": announcements
                })


@login_required
def cards(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        today = TimeMachine().today()

        flashcards = VocabularyManager().display_cards(
                client
                )

        cards_today = VocabularyManager().display_cards_studied_per_date(
                client,
                today
                )

        if request.method == "POST":
            if request.POST["action_on_cards"] == "open":
                card_id_raw = request.POST["card_id"]
                card_id = card_id_raw.split(": ")[0]

                return redirect("card", client=client, card_id=card_id)

        context = {
            "client": client,
            "flashcards": flashcards,
            "cards_today": cards_today
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, 'm_cards.html', context)
        else:
            return render(request, 'cards.html', context)


@login_required
def card(request, client, card_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        flashcard = VocabularyManager().display_card(
                card_id
                )

        if request.method == "POST":
            if request.POST["action_on_card"] == "remove":

                VocabularyManager().remove_card(card_id)

                return redirect("cards", client=client)

        context = {
            "client": client,
            "card_id": card_id,
            "flashcard": flashcard
            }

        return render(request, 'card.html', context)


@login_required
def flashcard(request, username, deck):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        flashcard = VocabularyManager().display_due_entries_json(
                current_user,
                deck
                )

        dark_mode = Client.objects.get(name=current_user).dark_mode

        if flashcard is None:
            return redirect("congratulations")

        else:
            return render(request, 'flashcard.html', {
                "deck": deck,
                "flashcard": flashcard,
                "dark_mode": dark_mode
                })


@login_required
def flashcard_question(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "GET":
            deck = request.GET["deck"]
            flashcard = VocabularyManager().display_due_entries_json(
                    current_user,
                    deck
                    )

            return HttpResponse(flashcard)


@login_required
def flashcard_answer(request):
    if request.method == 'GET':
        card_id = request.GET['card_id']
        answer = request.GET['answer']
        js_time = request.GET['card_opening_time']

        card_opening_time = TimeMachine().parse_js_time_to_system_time(
            js_time
            )

        VocabularyManager().update_card(
            card_id,
            answer,
            card_opening_time
            )

        return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


@login_required
def vocabulary(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return redirect(
            "flashcard",
            username=current_user,
            deck="vocabulary"
            )


@login_required
def sentences(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return redirect(
            "flashcard",
            username=current_user,
            deck="sentences"
            )


@login_required
def congratulations(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        reset_line = VocabularyManager().reset_line(current_user)
        messages.success(request, ("You're done for today!"))

        return render(request, 'congratulations.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            first_name = request.user.first_name
            last_name = request.user.last_name
            current_user = first_name + " " + last_name

            return redirect("campus")

        else:
            messages.error(request, ("Wrong password or username. Try again."))
            return redirect("login_user")

        return render(request, "campus.html", {})

    else:
        return render(request, "login_user.html", {})


@login_required
def logout_user(request):
    logout(request)

    return redirect("welcome")


@staff_member_required
def register_user(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            f_name = request.POST["first_name"]
            l_name = request.POST["last_name"]
            password = request.POST["password"]

            f_name = f_name.strip()
            l_name = l_name.strip()
            password = password.strip()

            username = f_name.lower() + l_name.lower()

            user = authenticate(
                    request,
                    username=username,
                    password=password
                    )

            output = ClientsManager().add_client_and_user(
                    f_name,
                    l_name,
                    password,
                    user
                    )

            messages.add_message(request, getattr(messages, output[0]), output[1])
            return redirect(output[2])

        return render(request, "register_user.html", {})


@staff_member_required
def register_client(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["edit"] == "save":

                user_type = request.POST["user_type"]
                name = request.POST["name"]
                phone_number = request.POST["phone_number"]
                contact_email_address = request.POST["contact_email_address"]
                meeting_duration = request.POST["meeting_duration"]    
                acquisition_channel = request.POST["acquisition_channel"]
                recommenders = request.POST["recommenders"]
                reasons_for_resignation = request.POST["reasons_for_resignation"]
                status = request.POST["status"]
                coach = request.POST["coach"]
                level = request.POST["level"]
                daily_limit_of_new_vocabulary = request.POST["daily_limit_of_new_vocabulary"]
                maximal_interval_vocabulary = request.POST["maximal_interval_vocabulary"]
                daily_limit_of_new_sentences = request.POST["daily_limit_of_new_sentences"]
                maximal_interval_sentences = request.POST["maximal_interval_sentences"]
                wage = request.POST["wage"]

                ClientsManager().edit_user(
                    user_type,
                    name,
                    phone_number,
                    contact_email_address,
                    meeting_duration,
                    acquisition_channel,
                    recommenders,
                    reasons_for_resignation,
                    status,
                    coach,
                    level,
                    daily_limit_of_new_vocabulary,
                    maximal_interval_vocabulary,
                    daily_limit_of_new_sentences,
                    maximal_interval_sentences,
                    wage
                    )

                return redirect("list_current_users")

        current_clients = ClientsManager().list_current_users()

        return render(request, "list_current_users.html", {
            "current_clients": current_clients
            })


@staff_member_required
def list_current_users(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_users()

        if request.method == "POST":
            if request.POST["action_on_user"] == "more":
                client = request.POST["client"]

                details = ClientsManager().load_user(client)

                return render(request, "user.html", {
                    "details": details
                    })

            elif request.POST["action_on_user"] == "edit":
                client = request.POST["client"]

                details = ClientsManager().load_user(client)
                coaches = ClientsManager().list_current_coaches()

                return render(request, "edit_user.html", {
                    "details": details,
                    "coaches": coaches
                    })

            elif request.POST["action_on_user"] == "update":
                user_type = request.POST["user_type"]
                client = request.POST["client"]
                phone_number = request.POST["phone_number"]
                contact_email_address = request.POST["contact_email_address"]
                meeting_duration = request.POST["meeting_duration"]    
                acquisition_channel = request.POST["acquisition_channel"]
                recommenders = request.POST["recommenders"]
                reasons_for_resignation = request.POST["reasons_for_resignation"]
                status = request.POST["status"]
                coach = request.POST["coach"]
                level = request.POST["level"]
                daily_limit_of_new_vocabulary = request.POST["daily_limit_of_new_vocabulary"]
                maximal_interval_vocabulary = request.POST["maximal_interval_vocabulary"]
                daily_limit_of_new_sentences = request.POST["daily_limit_of_new_sentences"]
                maximal_interval_sentences = request.POST["maximal_interval_sentences"]
                wage = request.POST["wage"]

                ClientsManager().edit_user(
                    user_type,
                    client,
                    phone_number,
                    contact_email_address,
                    meeting_duration,
                    acquisition_channel,
                    recommenders,
                    reasons_for_resignation,
                    status,
                    coach,
                    level,
                    daily_limit_of_new_vocabulary,
                    maximal_interval_vocabulary,
                    daily_limit_of_new_sentences,
                    maximal_interval_sentences,
                    wage
                    )

                return redirect("list_current_users")

            else:

                return render(request, "list_current_users.html", {
                    "clients": clients
                    })

        return render(request, "list_current_users.html", {
            "clients": clients
            })


@staff_member_required
def display_user(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        details = ClientsManager().load_user(client)

        return render(request, "display_user.html", {
            "details": details
            })


@login_required
def options(request, template_name="404"):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)

        client = Client.objects.get(name=current_user)
        daily_limit_of_new__vocabulary = client.daily_limit_of_new_vocabulary
        daily_limit_of_new_sentences = client.daily_limit_of_new_sentences
        maximal_interval_vocabulary = client.maximal_interval_vocabulary
        maximal_interval_sentences = client.maximal_interval_sentences
        dark_mode = client.dark_mode

        if request.method == "POST":
            if request.POST["action_on_client_option"] == "change_vocabulary_limit":
                new_limit = request.POST["daily_limit_of_new_vocabulary"]

                client.daily_limit_of_new_vocabulary = new_limit
                client.save()

                messages.success(request, ("Settings changed"))
                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_sentences_limit":
                new_limit = request.POST["daily_limit_of_new_sentences"]

                client.daily_limit_of_new_sentences = new_limit
                client.save()

                messages.success(request, ("Settings changed"))
                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_vocabulary_interval":
                new_limit = request.POST["maximal_interval_vocabulary"]

                client.maximal_interval_vocabulary = new_limit
                client.save()

                messages.success(request, ("Settings changed"))
                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_sentences_interval":
                new_limit = request.POST["maximal_interval_sentences"]

                client.maximal_interval_sentences = new_limit
                client.save()

                messages.success(request, ("Settings changed"))
                return redirect("options")

            elif request.POST["action_on_client_option"] == "turn_on_dark_mode":

                client.dark_mode = 1
                client.save()

                messages.success(request, ("Dark mode turned on"))
                return redirect("options")

            elif request.POST["action_on_client_option"] == "turn_off_dark_mode":

                client.dark_mode = 0
                client.save()

                messages.success(request, ("Dark mode turned off"))
                return redirect("options")

        context = {
            "daily_limit_of_new_vocabulary": daily_limit_of_new__vocabulary,
            "daily_limit_of_new_sentences": daily_limit_of_new_sentences,
            "maximal_interval_vocabulary": maximal_interval_vocabulary,
            "maximal_interval_sentences": maximal_interval_sentences,
            "dark_mode": dark_mode
        }

        if user_agent.is_mobile:
            return render(request, "m_options.html", context)

        else:
            return render(request, "options.html", context)


@staff_member_required
def staff(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        # Automatic processes
        ChallengeManager().plan_challenges()

        return render(request, "staff.html", {
            "current_user": current_user
            })


@staff_member_required
def old_staff(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "old_staff.html", {})


@staff_member_required
def management(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "management.html", {
            "current_user": current_user
            })


@staff_member_required
def upload_composer(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_upload"] == "upload":
                instance = Binder(binder=request.FILES["csv_file"], id=1)
                instance.save()

                return redirect("upload_composer")

            elif request.POST["action_on_upload"] == "save":
                file = Binder.objects.get(pk=1)
                with open(file.binder.path, "rb") as file:
                    file_converted = file.read().decode("utf8", errors="ignore")
                    rows = StringToCsv().convert(file_converted)

                    with transaction.atomic():
                        for row in rows:
                            list_number = row[0]
                            sentence_number = row[1]
                            sentence_id = row[2]
                            name = row[3]
                            polish = row[4]
                            english = row[5]
                            glossary = row[6]
                            submission_stamp = row[7]
                            submission_date = row[8]
                            status = row[9]
                            translation = row[10]
                            result = row[11]
                            reviewing_user = row[12]
                            set_id = row[13]
                            item = row[14]

                            SentenceManager().upload_sentence_lists(
                                list_number,
                                sentence_number,
                                sentence_id,
                                name,
                                polish,
                                english,
                                glossary,
                                submission_stamp,
                                submission_date,
                                status,
                                translation,
                                result,
                                reviewing_user,
                                set_id,
                                item
                                )

                    return redirect("upload_composer")

        return render(request, "upload_composer.html", {})


@login_required
def profile_menu(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "profile_menu.html", {})


@login_required
def portrait(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        courses = RoadmapManager().display_current_courses_by_client(
                client
                )

        profile = RoadmapManager().display_profile(client)
        display_name = profile[1]
        current_semester = profile[4]
        current_degree = profile[6]
        current_program = profile[29]

        target = StreamManager().display_activity_target(client)
        quaterly_points = StreamManager().display_activity(client)
        total_points = ActivityManager().get_points_over_lifetime_total(client)
        last_week_points = ActivityManager().get_points_last_week(
                client
                )

        context = {
            "courses": courses,
            "display_name": display_name,
            "current_semester": current_semester,
            "current_degree": current_degree,
            "current_program": current_program,
            "first_name": first_name,
            "target": target,
            "last_week_points": last_week_points,
            "quaterly_points": quaterly_points,
            "total_points": total_points
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_portrait.html", context)
        else:
            return render(request, "portrait.html", context)


@login_required
def profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        profile = RoadmapManager().display_profile(current_user)
        semesters = RoadmapManager().display_semesters(current_user)
        tags = BackOfficeManager().display_tags()
        stories = StreamManager().display_stories(current_user)

        if stories:

            return redirect("profile_introduction")

        if profile is None:
            display_name = current_user
            avatar = "https://docs.google.com/drawings/d/e/2PACX-1vQnrkWBZi2-ZrZ8fyKO_8qIBuOSrz19oeTq9XNnhCbDw6CAu8Rb8uBKYNcLBT0JLcZ8Dv_EWmZ93BBn/pub?w=685&h=686"
            current_semester = "1"
            current_degree = ""
            early_admission = 0

        elif profile[2] == "":
            display_name = profile[1]
            avatar = "https://docs.google.com/drawings/d/e/2PACX-1vQnrkWBZi2-ZrZ8fyKO_8qIBuOSrz19oeTq9XNnhCbDw6CAu8Rb8uBKYNcLBT0JLcZ8Dv_EWmZ93BBn/pub?w=685&h=686"
            current_semester = profile[4]
            current_degree = profile[6]
            early_admission = profile[7]

        else:
            display_name = profile[1]
            avatar = profile[2]
            current_semester = profile[4]
            current_degree = profile[6]
            early_admission = profile[7]

        if current_degree == "associate":
            semester_duration = 3
        else:
            semester_duration = 3

        degrees = RoadmapManager().display_degrees(current_user)
        current_degree_status = degrees.get(current_degree)
        courses = RoadmapManager().display_roadmap(current_user, current_semester)

        end_of_semester = BackOfficeManager().display_end_of_semester()
        activity_points = StreamManager().display_activity(current_user)
        target = StreamManager().display_activity_target(current_user)

        if request.method == "POST":
            if request.POST["action_on_profile"] == "more":
                # try:
                roadmap_id_number = request.POST["roadmap_id_number"]

                roadmap_details = RoadmapManager().display_roadmap_details(roadmap_id_number)
                course = roadmap_details[2]
                course_details = RoadmapManager().display_course(course)
                grades = RoadmapManager().display_grades(current_user, course)
                threshold = RoadmapManager().display_course_threshold(course)
                assessment_method = course_details[5]
                assessment_system = course_details[7]
                status_type = roadmap_details[9]
                deadline_number = roadmap_details[4]
                today_number = TimeMachine().today_number()

                if assessment_method == "statistics":
                    statistics = StreamManager().advanced_statistics(current_user)
                    result = statistics[assessment_system]

                elif assessment_method == "assignment":
                    if assessment_system == "item":

                        item = roadmap_details[7]
                        if item == -1:
                            result = "uncompleted"
                        else:
                            result = CurriculumManager().display_assignment_status(item)
                    elif assessment_system == "component_ids":
                        component_id = course_details[9]
                        result = CurriculumManager().display_assignment_status_by_component_id(component_id)

                else:
                    if assessment_system == "last_final":
                        result = RoadmapManager().display_last_final_grade(
                            current_user,
                            course
                            )
                    elif assessment_system == "average_final":
                        result = RoadmapManager().display_average_final_grade(
                            current_user,
                            course
                            )
                    elif assessment_system == "last_midterm":
                        result = RoadmapManager().display_last_midterm_grade(
                            current_user,
                            course
                            )
                    elif assessment_system == "average_midterm":
                        result = RoadmapManager().display_average_midterm_grade(
                            current_user,
                            course
                            )

                # Status: passed/ongoing/failed
                if status_type == "manual":
                    status = roadmap_details[6]
                else:
                    if assessment_method == "assignment":

                        if result == "completed":
                            status = "passed"

                        else:
                            if deadline_number > today_number:
                                status = "ongoing"
                            else:
                                status = "failed"

                    elif result >= threshold:
                        status = "passed"

                    elif result == -1:
                        status = "ongoing"

                    elif assessment_method == "statistics" or assessment_system == "average_midterm" or assessment_system == "average_final":

                        if deadline_number > today_number:
                            status = "ongoing"

                        else:
                            status = "failed"

                    else:
                        status = "failed"

                RoadmapManager().update_roadmap(roadmap_id_number, status)

                deadline = TimeMachine().number_to_system_date(roadmap_details[4])

                return render(request, "display_roadmap_details.html", {
                    "roadmap_details": roadmap_details,
                    "course_details": course_details,
                    "deadline": deadline,
                    "grades": grades,
                    "status": status,
                    "assessment_method": assessment_method,
                    "assessment_system": assessment_system,
                    "result": result
                    })

        if user_agent.is_mobile:
            return render(request, "m_profile.html", {
                "courses": courses,
                "display_name": display_name,
                "avatar": avatar,
                "current_degree": current_degree,
                "early_admission": early_admission,
                "semesters": semesters,
                "semester_duration": semester_duration,
                "current_degree_status": current_degree_status,
                "end_of_semester": end_of_semester,
                "activity_points": activity_points,
                "target": target,
                "tags": tags,
                })

        else:
            return render(request, "profile.html", {
                "courses": courses,
                "display_name": display_name,
                "avatar": avatar,
                "current_degree": current_degree,
                "early_admission": early_admission,
                "semesters": semesters,
                "semester_duration": semester_duration,
                "current_degree_status": current_degree_status,
                "end_of_semester": end_of_semester,
                "activity_points": activity_points,
                "target": target,
                "tags": tags,
                })


@login_required
def profile_introduction(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        stories = StreamManager().display_stories(current_user)

        if request.method == "POST":
            if request.POST["action_on_profile"] == "start_story":
                story = request.POST["story_number"]

                return redirect(
                    "display_spin",
                    client=current_user,
                    story=story
                    )

        return render(request, "profile_introduction.html", {
            "stories": stories,
            "first_name": first_name
            })


@login_required
def submit_assignment(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        assignment = CurriculumManager().display_assignment(item)
        client = assignment[3]
        assignment_type = assignment[6]

        if request.method == "POST":
            item = request.POST["item"]
            client = request.POST["client"]
            assignment_type = request.POST["assignment_type"]
            title = request.POST["title"]
            content = request.POST["content"]

            output = SubmissionManager().run_submission(
                    item,
                    client,
                    assignment_type,
                    title,
                    content,
                    current_user
                    )

            if output[2] != "applause":
                messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )

                return redirect(output[2])

            else:
                return redirect(output[2], activity_points=output[3])

        return render(request, "submit_assignment.html", {
                "item": item,
                "client": client,
                "assignment_type": assignment_type
                })


@login_required
def submit_assignment_automatically(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        assignment = CurriculumManager().display_assignment(item)
        client = assignment[3]
        assignment_type = assignment[6]

        if request.method == "POST":
            item = request.POST["item"]
            client = request.POST["client"]
            assignment_type = request.POST["assignment_type"]
            title = request.POST["title"]
            content = request.POST["content"]

            output = SubmissionManager().run_submission(
                    item,
                    client,
                    assignment_type,
                    title,
                    content,
                    current_user
                    )

            messages.add_message(
                    request,
                    getattr(messages, output[0]),
                    output[1]
                    )

            return redirect(output[2])

        return render(request, "submit_assignment_automatically.html", {
                "item": item,
                "client": client,
                "assignment_type": assignment_type
                })


@login_required
def translate_sentences(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        list_number = SentenceManager().find_list_number_by_item(item)
        sentences = SentenceManager().display_sentence_list(list_number)
        assignment = CurriculumManager().display_assignment(item)
        client = assignment[3]
        assignment_type = assignment[6]
        title = assignment[7]

        if request.method == "POST":
            if request.POST["action_on_submission"] == "translate":
                originals = request.POST.getlist("polish")
                translations = request.POST.getlist("english")
                sentence_numbers = request.POST.getlist("sentence_number")

                entries = [
                    (sentence_number, translation)
                    for sentence_number, translation
                    in zip(sentence_numbers, translations)
                    ]

                if assignment_type == "translation":
                    polish = " ".join(originals)
                    translation = " ".join(translations)
                    content = f"{polish}\n\n{translation}"

                else:
                    content_raw = [
                        f"{original}\n{translation}\n"
                        for original, translation
                        in zip(originals, translations)
                        ]

                    content = "\n".join(content_raw)

                # # Move this to the logic
                # Submitting sentence translations
                SentenceManager().submit_sentence_translation(entries)
                SubmissionManager().add_submission(
                    item,
                    client,
                    assignment_type,
                    title,
                    content
                    )

                # Tick off the task in student's to-do list
                CurriculumManager().change_status_to_completed(item, current_user)

                # Add information to stream to count Effort Hours
                StreamManager().add_to_stream(client, "T", 10, current_user)

                messages.success(request, ("Your assignment has been submitted!"))
                return redirect("campus")

        if assignment_type == "translation":
            return render(request, "translate_text.html", {
                    "item": item,
                    "client": client,
                    "sentences": sentences
                    })
        else:
            return render(request, "translate_sentences.html", {
                    "item": item,
                    "client": client,
                    "sentences": sentences
                    })


@login_required
def list_of_submissions(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        submissions = SubmissionManager().display_students_assignments_limited(
                current_user
                )
        tags = BackOfficeManager().display_tags()

        if request.method == "POST":
            unique_id = request.POST["unique_id"]

            submission = SubmissionManager().display_students_assignment(
                    unique_id
                    )

            date = submission[0]
            title = submission[1]
            status = submission[9]
            assignment_type = submission[10]
            item = submission[11]

            # Move it to the logic
            if assignment_type == "translation":
                list_number = SentenceManager().find_list_number_by_item(item)
                sentences = SentenceManager().display_graded_list(list_number)

                return render(request, "submission_entry_translation.html", {
                        "status": status,
                        "sentences": sentences
                        })

            elif assignment_type != "sentences":

                return render(request, "submission_entry.html", {
                        "submission": submission,
                        "tags": tags
                        })

            else:
                list_number = SentenceManager().find_list_number_by_item(item)
                sentences = SentenceManager().display_graded_list(list_number)

                return render(request, "submission_entry_sentences.html", {
                        "title": title,
                        "date": date,
                        "status": status,
                        "sentences": sentences
                        })

        if user_agent.is_mobile:
            return render(request, "m_my_assignments.html", {
                "submissions": submissions
                })

        else:
            return render(request, "list_of_submissions.html", {
                "submissions": submissions
                })


@staff_member_required
def list_of_assignments_to_grade(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        essays = SubmissionManager().assignments_to_grade()

        if request.method == "POST":
            if request.POST["revision_action"] == "grade_assignment":
                unique_id = request.POST["unique_id"]
                essay = SubmissionManager().display_assignment(unique_id)

                return render(request, "grade_assignment.html", {
                    "essay": essay
                    })

            elif request.POST["revision_action"] == "save_graded_assignment":
                unique_id = request.POST["unique_id"]
                reviewed_content = request.POST["reviewed_content"]
                conditions = request.POST["conditions"]
                comment = request.POST["comment"]
                grade = request.POST["grade"]

                save_revision = SubmissionManager().grade_assignment(
                    unique_id,
                    reviewed_content,
                    current_user,
                    conditions,
                    comment,
                    grade
                    )

                return render(request, "list_of_assignments_to_grade.html", {
                    "essays": essays
                    })

            elif request.POST["revision_action"] == "save_and_mark_graded_assignment":
                unique_id = request.POST["unique_id"]
                reviewed_content = request.POST["reviewed_content"]
                conditions = request.POST["conditions"]
                comment = request.POST["comment"]
                grade = request.POST["grade"]

                mark_as_graded = SubmissionManager().mark_as_graded(unique_id)

                save_revision = SubmissionManager().grade_assignment(
                    unique_id,
                    reviewed_content,
                    current_user,
                    conditions,
                    comment,
                    grade
                    )

                return redirect("list_of_assignments_to_grade")

        return render(request, "list_of_assignments_to_grade.html", {
            "essays": essays
            })


@staff_member_required
def grade_assignment(request, unique_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        essay = SubmissionManager().display_assignment(unique_id)

        if request.method == "POST":
            if request.POST["revision_action"] == "save_graded_assignment":
                unique_id = request.POST["unique_id"]
                reviewed_content = request.POST["reviewed_content"]
                conditions = request.POST["conditions"]
                comment = request.POST["comment"]
                grade = request.POST["grade"]

                save_revision = SubmissionManager().grade_assignment(
                    unique_id,
                    reviewed_content,
                    current_user,
                    conditions,
                    comment,
                    grade
                    )

                return redirect("list_of_assignments_to_grade")

            elif request.POST["revision_action"] == "save_and_mark_graded_assignment":
                unique_id = request.POST["unique_id"]
                reviewed_content = request.POST["reviewed_content"]
                conditions = request.POST["conditions"]
                comment = request.POST["comment"]
                grade = request.POST["grade"]

                mark_as_graded = SubmissionManager().mark_as_graded(unique_id)

                save_revision = SubmissionManager().grade_assignment(
                    unique_id,
                    reviewed_content,
                    current_user,
                    conditions,
                    comment,
                    grade
                    )

                return redirect("list_of_assignments_to_grade")

        return render(request, "grade_assignment.html", {
            "essay": essay
            })


@staff_member_required
def upload_curriculum(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                CurriculumManager().add_curriculum(
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4],
                    entry[5],
                    entry[6],
                    entry[7],
                    entry[8],
                    entry[9],
                    entry[10]
                    )

            messages.success(request, ("The file has been uploaded!"))
            return redirect("upload_curriculum")

        return render(request, "upload_curriculum.html", {})


@staff_member_required
def add_curriculum(request, client=""):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        names = ClientsManager().list_current_clients()
        modules = CurriculumManager().display_modules()
        module_status = 0

        if request.method == "POST":
            if request.POST["curriculum_action"] == "choose_other_modules":
                name = request.POST["name"]
                component_id = request.POST["component_id"]

                module_status = 1
                assignment_type_raw = re.search(r"\w.+_", component_id).group()
                assignment_type = re.sub("_", "", assignment_type_raw)
                names = [name]

                module = CurriculumManager().display_module(component_id)

                return render(request, "add_curriculum_2.html", {
                    "client": name,
                    "names": names,
                    "assignment_type": assignment_type,
                    "modules": modules,
                    "module": module,
                    "module_status": module_status,
                    "component_id": component_id
                    })

            else:
                deadline = request.POST["deadline"]
                client = request.POST["client"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                content = request.POST["content"]
                matrix = "custom matrix"
                reference = request.POST["reference"]
                resources = request.POST["resources"]
                conditions = request.POST["conditions"]
                component_id = request.POST["component_id"]

                CurriculumPlanner().plan_curriculum(
                    deadline,
                    client,
                    component_id,
                    assignment_type,
                    title,
                    content,
                    matrix,
                    resources,
                    conditions,
                    reference
                    )

                messages.success(request, ("Module added to curricula!"))
                return redirect("add_curriculum")

        return render(request, "add_curriculum.html", {
            "client": client,
            "names": names,
            "modules": modules,
            "module_status": module_status
            })


@staff_member_required
def add_multiple_curricula(request, client=""):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        modules = CurriculumManager().display_modules()

        if request.method == "POST":
            if request.POST["curriculum_action"] == "choose_other_modules":
                component_id = request.POST["component_id"]

                return redirect(
                    "add_multiple_curricula_2",
                    component_id=component_id
                    )

        return render(request, "add_multiple_curricula.html", {
            "modules": modules
            })


@staff_member_required
def add_multiple_curricula_2(request, component_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        module = CurriculumManager().display_module(component_id)

        if request.method == "POST":
            if request.POST["curricula_action"] == "plan_curricula":        
                deadline = request.POST["deadline"]
                clients = request.POST.getlist("client")
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                content = request.POST["content"]
                matrix = "custom matrix"
                reference = request.POST["reference"]
                resources = request.POST["resources"]
                conditions = request.POST["conditions"]

                CurriculumPlanner().plan_multiple_curricula(
                    deadline,
                    clients,
                    component_id,
                    assignment_type,
                    title,
                    content,
                    matrix,
                    resources,
                    conditions,
                    reference
                    )

                messages.success(request, ("Module added to curricula!"))
                return redirect("add_multiple_curricula")

        return render(request, "add_multiple_curricula_2.html", {
            "component_id": component_id,
            "clients": clients,
            "module": module
            })


@staff_member_required
def remove_multiple_curricula(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        modules = CurriculumManager().display_modules()

        if request.method == "POST":
            if request.POST["action_on_curricula"] == "remove":
                clients = request.POST.getlist("client")
                component_id = request.POST["component_id"]
                deadline = request.POST["deadline"]

                CurriculumPlanner().remove_multiple_curricula(
                        clients,
                        component_id,
                        deadline
                        )

                messages.success(request, ("Curricula removed"))
                return redirect("remove_multiple_curricula")

        return render(request, "remove_multiple_curricula.html", {
            "clients": clients,
            "modules": modules
            })


@login_required
def assignments(request, client=''):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        score = ActivityManager().calculate_points_this_week(current_user)
        ratings = RatingManager().display_unrated(current_user)

        uncomplated_assignments = CurriculumManager().display_uncompleted_assignments(current_user)
        complated_assignments = CurriculumManager().display_completed_assignments(current_user)

        if user_agent.is_mobile:
            return render(request, "m_my_to_do_list.html", {
                "uncomplated_assignments": uncomplated_assignments,
                "complated_assignments": complated_assignments,
                "score": score,
                "ratings": ratings
                })

        else:
            return render(request, "assignments.html", {
                "uncomplated_assignments": uncomplated_assignments,
                "complated_assignments": complated_assignments,
                "score": score,
                "ratings": ratings
                })


@login_required
def assignment(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")
        assignment = CurriculumManager().display_assignment(item)

        if request.method == "POST":
            action = request.POST["action_on_assignment"]

            product = HomeworkManager().choose_action(
                    item,
                    current_user,
                    action
                    )

            if len(product) > 2:
                messages.add_message(
                        request,
                        getattr(messages, product[2][0]),
                        product[2][1]
                        )

            elif product[0] == "campus":
                messages.add_message(
                        request,
                        getattr(messages, product[1][0]),
                        product[1][1]
                        )

                return redirect(product[0])

            return redirect(product[0], product[1])

        if user_agent.is_mobile:
            return render(request, "m_assignment.html", {
                "item": item,
                "assignment": assignment
                })

        else:
            return render(request, "assignment.html", {
                "item": item,
                "assignment": assignment
                })


@login_required
def my_pronunciation(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entries = KnowledgeManager().display_pronunciation(current_user)
        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_pronunciation.html", {
                    "entries": entries
                    })

        else:
            return render(request, "my_pronunciation.html", {
                "entries": entries
                })


@staff_member_required
def deactivate_pronunciation_entries(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        context = {"clients": clients}

        if request.method == "POST":
            if request.POST["action_on_pronunciation"] == "remove":
                client = request.POST["client"]

                output = KnowledgeManager().deactivate_pronunciation(
                    client
                    )

                messages.add_message(
                    request,
                    getattr(messages, output[0]),
                    output[1]
                    )

                return redirect("deactivate_pronunciation_entries")

        return render(request, "deactivate_pronunciation_entries.html", context)


@staff_member_required
def display_curricula(request, client=None):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if client is not None:
            assignments = CurriculumManager().display_assignments_for_student(client)
        else:
            assignments = []

        if request.method == "POST":
            if request.POST["action_on_curriculum"] == "filter":
                client = request.POST["client"]

                return redirect("display_curricula", client=client)

            elif request.POST["action_on_curriculum"] == "more":
                item = request.POST["item"]

                return redirect("assignment", item=item)

            elif request.POST["action_on_curriculum"] == "remove":
                item = request.POST["item"]

                CurriculumManager().remove_curriculum(item)

                messages.success(request, ("Removed"))
                return redirect("display_curricula", client=client)

        return render(request, "display_curricula.html", {
            "client": client,
            "clients": clients,
            "assignments": assignments
            })


@staff_member_required
def display_modules(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        modules = CurriculumManager().display_modules()

        if request.method == "POST":
            if request.POST["action_on_module"] == "more":
                component_id = request.POST["component_id"]

                module = CurriculumManager().display_module(component_id)

                return render(request, "display_module.html", {
                    "module": module
                    })

            elif request.POST["action_on_module"] == "update":
                component_id = request.POST["component_id"]

                return redirect("update_module", component_id=component_id)

        return render(request, "display_modules.html", {
            "modules": modules
            })


@staff_member_required
def choose_component(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        components = KnowledgeManager().display_prompts("components")

        if request.method == "POST":
            component = request.POST["component"]

            return redirect("choose_id_prefix", component=component)

        return render(request, "choose_component.html", {
            "components": components
            })


@staff_member_required
def choose_id_prefix(request, component):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        prefixes = CurriculumManager().display_prefixes()

        if request.method == "POST":
            id_prefix = request.POST["id_prefix"]

            if (component == "sentences" or
                component == "translation" or
                component == "reading" or
                component == "survey" or
                component == "catalogue" or
                    component == "quiz"):

                return redirect(
                    "choose_reference",
                    component=component,
                    id_prefix=id_prefix
                    )
            else:
                return redirect(
                    "choose_resources",
                    component=component,
                    id_prefix=id_prefix,
                    reference=0
                    )

        return render(request, "choose_id_prefix.html", {
            "component": component,
            "prefixes": prefixes
            })


@staff_member_required
def choose_reference(request, component, id_prefix):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if component == "reading":
            references = BackOfficeManager().display_library()
        elif component == "sentences":
            references = SentenceManager().display_sets_by_type("sentences")
        elif component == "translation":
            references = SentenceManager().display_sets_by_type("translation")
        elif component == "survey":
            references = SurveyManager().display_surveys()
        elif component == "catalogue":
            references = KnowledgeManager().display_all_catalogues()
        elif component == "quiz":
            references = QuizManager().display_collection_ids()

        if request.method == "POST":
            reference = request.POST["reference"]

            if component == "reading":

                data = BackOfficeManager().find_position_in_library(reference)
                resources = data[3]

                return redirect(
                    "add_module",
                    component=component,
                    id_prefix=id_prefix,
                    reference=reference,
                    resources=resources
                    )

            else:

                resources = "-"

                return redirect(
                    "add_module",
                    component=component,
                    id_prefix=id_prefix,
                    reference=reference,
                    resources=resources
                    )

        return render(request, "choose_reference.html", {
            "component": component,
            "id_prefix": id_prefix,
            "references": references
            })


@staff_member_required
def choose_resources(request, component, id_prefix, reference):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            resources = request.POST["resources"]

            return redirect(
                "add_module",
                component=component,
                id_prefix=id_prefix,
                reference=reference,
                resources=resources
                )

        return render(request, "choose_resources.html", {
            "component": component,
            "id_prefix": id_prefix,
            "reference": reference
            })


@staff_member_required
def add_module(request, component, id_prefix, reference, resources):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        next_id_suffix = CurriculumManager().next_id_suffix(component, id_prefix)

        if request.method == "POST":
            id_prefix = request.POST["id_prefix"]
            id_suffix = request.POST["id_suffix"]
            title = request.POST["title"]
            content = request.POST["content"]
            conditions = request.POST["conditions"]

            id_suffix = int(id_suffix)
            component_id = f"{component}_{id_prefix}{id_suffix:02d}"

            CurriculumManager().add_module(
                component_id,
                component,
                title,
                content,
                resources,
                conditions,
                reference
                )

            messages.success(request, ("You have added a module!"))
            return redirect("choose_component")

        return render(request, "add_module.html", {
            "component": component,
            "id_prefix": id_prefix,
            "reference": reference,
            "resources": resources,
            "next_id_suffix": next_id_suffix
            })


@staff_member_required
def update_module(request, component_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        module = CurriculumManager().display_module(component_id)

        if request.method == "POST":
            if request.POST["action_on_curriculum"] == "update":
                component_id = request.POST["component_id"]
                component_type = request.POST["component_type"]
                title = request.POST["title"]
                content = request.POST["content"]
                resources = request.POST["resources"]
                conditions = request.POST["conditions"]
                reference = request.POST["reference"]

                CurriculumManager().update_module(
                    component_id,
                    component_type,
                    title,
                    content,
                    resources,
                    conditions,
                    reference
                    )

                messages.success(request, ("Module updated!"))
                return redirect("display_modules")

        return render(request, "update_module.html", {
            "module": module
            })


@staff_member_required
def display_matrices(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = CurriculumManager().display_matrices()

        if request.method == "POST":
            if request.POST["action_on_matrix"] == "filter":
                matrix = request.POST["matrix"]
                modules = CurriculumManager().display_matrix(matrix)

                return render(request, "display_matrices.html", {
                    "modules": modules,
                    "matrices": matrices
                    })

            elif request.POST["action_on_matrix"] == "more":
                component_id = request.POST["component_id"]

                return redirect("update_module", component_id=component_id)

            elif request.POST["action_on_matrix"] == "remove":
                component_id = request.POST["component_id"]
                matrix = request.POST["matrix"]
                limit_number = request.POST["limit_number"]

                CurriculumManager().remove_module_from_matrix(
                    matrix,
                    component_id,
                    limit_number
                    )

                return redirect("display_matrices")

        return render(request, "display_matrices.html", {
            "matrices": matrices
            })


@staff_member_required
def add_matrix(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        components = CurriculumManager().display_components()
        prefixes = CurriculumManager().display_prefixes()

        if request.method == "POST":
            component_id = request.POST["component_id"]
            matrix = request.POST["matrix"]
            week = request.POST["week"]
            day = request.POST["day"]

            limit_number = ((int(week) - 1) * 7) + int(day)

            CurriculumManager().add_matrix(
                component_id,
                matrix,
                limit_number
                )

            messages.success(request, ("You have updated the matrix!"))
            return redirect("add_matrix")

        return render(request, "add_matrix.html", {
            "components": components,
            "prefixes": prefixes
            })


@staff_member_required
def plan_matrix(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = CurriculumManager().display_matrices()
        clients = ClientsManager().list_current_clients()
        sundays = TimeMachine().display_sundays()

        if request.method == "POST":
            client = request.POST["client"]
            matrix = request.POST["matrix"]
            starting_date_number = request.POST["starting_date_number"]

            CurriculumPlanner().plan_curricula(
                client,
                matrix,
                starting_date_number
                )

            messages.success(request, ("You have planned a curriculum!"))
            return redirect("plan_matrix")

        return render(request, "plan_matrix.html", {
            "matrices": matrices,
            "clients": clients,
            "sundays": sundays
            })


@staff_member_required
def update_matrix(request, matrix):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrix_details = CurriculumManager().display_matrix(matrix)

        if request.method == "POST":
            new_matrix = request.POST["new_matrix"]
            old_matrix = request.POST["old_matrix"]

            CurriculumManager().update_matrix(
                new_matrix,
                old_matrix
                )

            id_prefix = CurriculumManager().display_prefix_by_matrix(old_matrix)
            CurriculumManager().change_matrix_name(new_matrix, id_prefix)

            return redirect("display_prefixes")

        return render(request, "update_matrix.html", {
            "matrix": matrix,
            "matrix_details": matrix_details
            })


@staff_member_required
def add_id_prefix(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        next_id_prefix = CurriculumManager().next_id_prefix()

        if request.method == "POST":
            if request.POST["action_on_id_prefix"] == "add":
                matrix = request.POST["matrix"]
                next_id_prefix = request.POST["next_id_prefix"]

                CurriculumManager().add_id_prefix(
                    matrix,
                    next_id_prefix
                    )

                return redirect("display_prefixes")

        return render(request, "add_id_prefix.html", {
            "next_id_prefix": next_id_prefix
            })


@staff_member_required
def display_prefixes(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        prefixes = CurriculumManager().display_prefixes()

        if request.method == "POST":
            if request.POST["action_on_matrix"] == "more":
                matrix = request.POST["matrix"]

                return redirect("update_matrix", matrix=matrix)

        return render(request, "display_prefixes.html", {
            "prefixes": prefixes
            })


@staff_member_required
def coach(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)

        context = {
            "current_user": current_user,
            "current_client": current_client
            }

        return render(request, "coach.html", context)


@staff_member_required
def teacher(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        context = {"current_user": current_user}

        return render(request, "teacher.html", context)


@staff_member_required
def coach_menu(request):
    return render(request, "coach_menu.html", {})


@staff_member_required
def switch_clients(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            client = request.POST["client"]
            switch = CurrentClientsManager().switch_current_client(current_user, client)

            messages.success(request, (f"You've picked {client}!"))
            return redirect("agenda")

        current_client = CurrentClientsManager().current_client(current_user)
        clients = ClientsManager().list_current_clients()

        if current_client in clients:
            clients.remove(current_client)

        return render(request, "switch_clients.html", {
            "current_client": current_client,
            "clients": clients
            })


@staff_member_required
def session_mode(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        prompts = KnowledgeManager().display_prompts("memories")
        memories = KnowledgeManager().display_all_memories()
        wordbook = KnowledgeManager().display_wordbook()
        sentencebook = KnowledgeManager().display_sentencebook()
        catalogues = KnowledgeManager().display_all_catalogues()
        pronunciation = KnowledgeManager().display_all_pronunciation()

        if request.method == "POST":
            last_form = request.POST["add_knowledge"].replace("add_", "")
            if request.POST["add_knowledge"] == "add_pronunciation":
                entry = request.POST["pronunciation_entry"]

                current_client = CurrentClientsManager().current_client(current_user)
                in_pronunciation = KnowledgeManager().check_if_in_pronunciation(current_client, entry)
                if len(in_pronunciation) == 0:

                    KnowledgeManager().add_pronunciation(current_client, entry, current_user)

                    return render(request, "session_mode.html", {
                        "current_client": current_client,
                        "last_form": last_form,
                        "catalogues": catalogues,
                        "pronunciation": pronunciation,
                        "sentencebook": sentencebook,
                        "wordbook": wordbook,
                        "prompts": prompts,
                        "memories": memories
                        })

                else:
                    messages.error(request, ("Such entry already exists."))
                    return render(request, "session_mode.html", {
                        "current_client": current_client,
                        "last_form": last_form,
                        "catalogues": catalogues,
                        "pronunciation": pronunciation,
                        "sentencebook": sentencebook,
                        "wordbook": wordbook,
                        "prompts": prompts,
                        "memories": memories
                        })

            elif request.POST["add_knowledge"] == "add_wordbook":
                entry = request.POST["wordbook_entry"]

                KnowledgeManager().add_to_book(
                    current_client,
                    entry,
                    current_user,
                    "vocabulary"
                    )

                return redirect("session_mode")

            elif request.POST["add_knowledge"] == "add_sentencebook":
                entry = request.POST["sentencebook_entry"]

                add_to_wordbook = KnowledgeManager().add_to_book(current_client, entry, current_user, "sentences")

                return render(request, "session_mode.html", {
                        "current_client": current_client,
                        "last_form": last_form,
                        "catalogues": catalogues,
                        "pronunciation": pronunciation,
                        "sentencebook": sentencebook,
                        "wordbook": wordbook,
                        "prompts": prompts,
                        "memories": memories
                        })

            elif request.POST["add_knowledge"] == "add_memories":
                prompt = request.POST["memories_prompt"]
                left_option = request.POST["left_option"]
                right_option = request.POST["right_option"]

                check = KnowledgeManager().check_if_in_memories(
                        current_client,
                        prompt,
                        left_option,
                        right_option
                        )

                if check is True:
                    messages.error(request, ("Such a memory already exists"))
                    return redirect("session_mode")

                KnowledgeManager().add_memory(
                    current_user,
                    current_client,
                    prompt,
                    left_option,
                    right_option
                    )

                return render(request, "session_mode.html", {
                        "current_client": current_client,
                        "last_form": last_form,
                        "catalogues": catalogues,
                        "pronunciation": pronunciation,
                        "sentencebook": sentencebook,
                        "wordbook": wordbook,
                        "prompts": prompts,
                        "memories": memories
                        })

            elif request.POST["add_knowledge"] == "add_catalogues":
                entry = request.POST["catalogues_entry"]

                output = KnowledgeManager().add_catalogue_to_book(
                    current_client,
                    entry,
                    current_user,
                    "vocabulary"
                    )

                messages.add_message(
                    request,
                    getattr(messages, output[0]),
                    output[1]
                    )

                return redirect("session_mode")

            else:
                pass

    return render(request, "session_mode.html", {
        "current_client": current_client,
        "catalogues": catalogues,
        "pronunciation": pronunciation,
        "sentencebook": sentencebook,
        "wordbook": wordbook,
        "prompts": prompts,
        "memories": memories
        })


@staff_member_required
def upload_dictionary(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                publication_date = TimeMachine().date_to_number(entry[3])
                add_to_dictionary = KnowledgeManager().upload_dictionary(
                    entry[0],
                    entry[1],
                    entry[2],
                    publication_date,
                    entry[4]
                    )

            messages.success(request, ("The file has been uploaded!"))
            return render(request, "upload_dictionary.html", {})

        return render(request, "upload_dictionary.html", {})


@staff_member_required
def dictionary(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        dictionary = KnowledgeManager().display_dictionary()

        return render(request, "dictionary.html", {"dictionary": dictionary})


@staff_member_required
def translate_wordbook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = KnowledgeManager().display_open_book("vocabulary")
        counter = KnowledgeManager().count_open_book("vocabulary")

        if entry is None:
            messages.success(request, ("You've translated all the wordbook entries!"))
            return render(request, "translate_wordbook.html", {})

        if request.method == "POST":
            if request.POST["wordbook_action"] == "delete":
                english = request.POST["english"]

                KnowledgeManager().delete_book_entries_by_english(english)

                return redirect("translate_wordbook")

            elif request.POST["wordbook_action"] == "save":
                english = request.POST["english"]
                polish = request.POST["polish"]
                comment = request.POST["comment"]

                KnowledgeManager().translate_book_entry(
                        entry[1],
                        english,
                        polish,
                        current_user
                        )

                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("translate_wordbook")

            elif request.POST["wordbook_action"] == "return":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().return_book_entry(current_user, english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("translate_wordbook")

        return render(request, "translate_wordbook.html", {
                "entry": entry,
                "counter": counter
                })


@staff_member_required
def approve_wordbook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = KnowledgeManager().display_translated_book("vocabulary")
        counter = KnowledgeManager().count_translated_book("vocabulary")

        if entry is None:
            messages.success(request, ("You've approved all the wordbook entries!"))
            return render(request, "approve_wordbook.html", {})

        if request.method == "POST":
            if request.POST["wordbook_action"] == "reject":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().reject_book_entry(english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("approve_wordbook")

            elif request.POST["wordbook_action"] == "approve":
                unique_id = request.POST["unique_id"]
                english = request.POST["english"]

                KnowledgeManager().approve_book_entry(unique_id, english, current_user)

                return redirect("approve_wordbook")

            elif request.POST["wordbook_action"] == "return":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().return_book_entry(current_user, english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("approve_wordbook")

        return render(request, "approve_wordbook.html", {
                "entry": entry,
                "counter": counter
                })


@staff_member_required
def translate_sentencebook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = KnowledgeManager().display_open_book("sentences")
        counter = KnowledgeManager().count_open_book("sentences")

        if entry is None:
            messages.success(request, ("You've translated all the sentencebook entries!"))
            return render(request, "translate_sentencebook.html", {})

        if request.method == "POST":
            if request.POST["sentencebook_action"] == "delete":
                english = request.POST["english"]

                KnowledgeManager().delete_book_entries_by_english(english)

                return redirect("translate_sentencebook")

            elif request.POST["sentencebook_action"] == "save":
                english = request.POST["english"]
                polish = request.POST["polish"]
                comment = request.POST["comment"]

                KnowledgeManager().translate_book_entry(
                        entry[1],
                        english,
                        polish,
                        current_user
                        )

                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("translate_sentencebook")

            elif request.POST["sentencebook_action"] == "return":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().return_book_entry(current_user, english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("translate_sentencebook")

        return render(request, "translate_sentencebook.html", {
                "entry": entry,
                "counter": counter
                })


@staff_member_required
def approve_sentencebook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = KnowledgeManager().display_translated_book("sentences")
        counter = KnowledgeManager().count_translated_book("sentences")

        if entry is None:
            messages.success(request, ("You've approved all the sentencebook entries!"))
            return render(request, "approve_sentencebook.html", {})

        if request.method == "POST":
            if request.POST["sentencebook_action"] == "reject":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().reject_book_entry(english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("approve_sentencebook")

            elif request.POST["sentencebook_action"] == "approve":
                unique_id = request.POST["unique_id"]
                english = request.POST["english"]

                KnowledgeManager().approve_book_entry(
                        unique_id,
                        english,
                        current_user
                        )

                return redirect("approve_sentencebook")

            elif request.POST["sentencebook_action"] == "return":
                english = request.POST["english"]
                comment = request.POST["comment"]

                KnowledgeManager().return_book_entry(current_user, english)
                KnowledgeManager().comment_on_book_entry(english, comment)

                return redirect("approve_sentencebook")

        return render(request, "approve_sentencebook.html", {
                "entry": entry,
                "counter": counter
                })


@staff_member_required
def review_book(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = KnowledgeManager().display_returned_book(
                current_user
                )
        counter = KnowledgeManager().count_returned_book(
                current_user
                )

        if entry is None:
            messages.success(request, ("You've reviewed all the wordbook entries!"))
            return render(request, "review_book.html", {})

        if request.method == "POST":
            if request.POST["book_action"] == "delete":
                english = request.POST["english_old"]

                KnowledgeManager().delete_book_entries_by_english(english)

                return redirect("review_book")

            elif request.POST["book_action"] == "correct":
                english_old = request.POST["english_old"]
                english_new = request.POST["english_new"]

                KnowledgeManager().correct_book_entry(
                        english_old,
                        english_new
                        )

                return redirect("review_book")

        return render(request, "review_book.html", {
                "entry": entry,
                "counter": counter
                })


@staff_member_required
def upload_anki(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["action_on_anki"] == "upload":
                instance = Binder(binder=request.FILES["csv_file"], id=1)
                instance.save()

                messages.success(request, ("File uploaded"))
                return render(request, "upload_anki.html", {
                    "clients": clients
                    })

            elif request.POST["action_on_anki"] == "save":
                cards = []

                file = Binder.objects.get(pk=1)
                with open(file.binder.path, "rb") as file:
                    file_converted = file.read().decode("utf8", errors="ignore")
                    entries = StringToCsv().convert(file_converted)
                    count = len(entries)

                    last_card_id = Card.objects.order_by("-card_id").first()

                    for entry in entries:
                        new_card = Card(
                            card_id=int(entry[0]) + last_card_id.card_id,
                            client=entry[1],
                            deck=entry[2],
                            polish=entry[3],
                            english=entry[4],
                            publication_date=entry[5],
                            due_date=entry[6],
                            interval=entry[7],
                            number_of_reviews=entry[8],
                            line=entry[9],
                            coach=entry[10],
                            initiation_date=entry[11]
                            )

                        cards.append(new_card)

                new_cards = Card.objects.bulk_create(cards)
                Binder.objects.get(pk=1).delete()

                messages.success(request, (f"{count} flashcards added"))
                return redirect("upload_anki")

        return render(request, "upload_anki.html", {
            "clients": clients
            })

# Highly destructive actions


@staff_member_required
def remove_all_new_cards(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        context = {"clients": clients}

        if request.method == "POST":
            if request.POST["action_on_cards"] == "remove":
                client = request.POST["client"]

                VocabularyManager().remove_all_new_cards(client)

                messages.success(request, (f"Flashcards removed"))
                return redirect("remove_all_new_cards")

        return render(request, "remove_all_new_cards.html", context)


@staff_member_required
def remove_profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profiles = RoadmapManager().display_profiles()

        if request.method == "POST":
            if request.POST["action_on_profile"] == "remove":
                profile = request.POST["profile"]

                Profile.objects.get(name=profile).delete()

                messages.success(request, ("Profile removed"))
                return redirect("remove_profile")

        return render(request, "remove_profile.html", {
            "profiles": profiles
            })


@staff_member_required
def remove_client(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_all_users()

        if request.method == "POST":
            if request.POST["action_on_client"] == "remove":
                client = request.POST["client"]

                Client.objects.get(name=client).delete()

                messages.success(request, ("Client removed"))
                return redirect("remove_client")

        return render(request, "remove_client.html", {
            "clients": clients
            })


@staff_member_required
def upload_catalogues(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                publication_date = TimeMachine().date_to_number(entry[0])
                add_to_dictionary = KnowledgeManager().upload_catalogues(
                    publication_date,
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4],
                    entry[5]
                    )

            messages.success(request, ("The file has been uploaded!"))

            return render(request, "upload_catalogues.html", {})

        return render(request, "upload_catalogues.html", {})


@staff_member_required
def catalogues(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        catalogues = KnowledgeManager().display_catalogues()

        if request.method == "POST":
            if request.POST["go_to"] == "details":

                return render(request, "catalogues_list_of_phrases.html", {
                    "catalogue_title": catalogue_title,
                    "phrases": phrases
                    })

        return render(request, "catalogues.html", {
            "catalogues": catalogues
            })


@staff_member_required
def catalogues_list_of_phrases(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            catalogue_number = request.POST["catalogue_number"]
            catalogue_title = request.POST["catalogue_title"]

            phrases = KnowledgeManager().display_list_of_phrases_in_catalogue(
                catalogue_number
                )

            return render(request, "catalogues_list_of_phrases.html", {
                "catalogue_title": catalogue_title,
                "phrases": phrases
                })


@staff_member_required
def prompts(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        prompts = KnowledgeManager().display_all_prompts()

        if request.method == "POST":
            if request.POST["prompts_action"] == "delete_prompt":
                prompt = request.POST["prompt"]
                parent = request.POST["parent"]

                delete_prompt = KnowledgeManager().delete_prompt(prompt, parent)

                return redirect("prompts")

            elif request.POST["prompts_action"] == "add_prompt":

                prompt = request.POST["prompt"]
                parent = request.POST["parent"]
                pattern = request.POST["pattern"]

                check_if_in_prompts = KnowledgeManager().check_if_in_prompts(prompt, parent)

                if check_if_in_prompts is False:
                    add_prompt = KnowledgeManager().add_prompt(
                        prompt,
                        parent,
                        pattern
                        )

                    messages.success(request, ("The prompt has been added!"))
                    return redirect("prompts")

                else:
                    messages.error(request, ("The prompt already exists!"))
                    return redirect("prompts")

            else:
                pass

        return render(request, "prompts.html", {
            "prompts": prompts
            })


@login_required
def memories(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        memories = KnowledgeManager().display_memories(current_user)
        if user_agent.is_mobile:
            return render(request, "m_memories.html", {
                "memories": memories
                })

        else:
            return render(request, "memories.html", {
                "memories": memories
                })


@staff_member_required
def upload_memories(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        # if request.method == "POST":
        #     csv_file = request.FILES["csv_file"]

        #     file = csv_file.read().decode("utf8")
        #     entries = StringToCsv().convert(file)

        #     for entry in entries:
        #         KnowledgeManager().add_memory(
        #             entry[0],
        #             entry[1],
        #             entry[2],
        #             entry[3],
        #             entry[4]
        #             )

        #     messages.success(request, ("The file has been uploaded!"))
            # return redirect("upload_memories")

        if request.method == "POST":
            if request.POST["action_on_upload"] == "upload":
                instance = Binder(binder=request.FILES["csv_file"], id=1)
                instance.save()

                messages.success(request, ("File uploaded"))
                return render(request, "upload_memories.html", {})

            elif request.POST["action_on_upload"] == "save":
                rows = []

                file = Binder.objects.get(pk=1)
                with open(file.binder.path, "rb") as file:
                    file_converted = file.read().decode("utf8", errors="ignore")
                    entries = StringToCsv().convert(file_converted)
                    count = len(entries)

                    now_number = TimeMachine().now_number()
                    today_number = TimeMachine().today_number()

                    for entry in entries:
                        new_row = Memory(
                            publication_stamp=now_number,
                            publication_date=entry[0],
                            coach=entry[1],
                            name=entry[2],
                            prompt=entry[3],
                            left_option=entry[4],
                            right_option=entry[5] if len(entry) == 6 else "",
                            due_date=today_number,
                            number_of_reviews=0,
                            answers="",
                            revision_days=""
                            )

                        rows.append(new_row)

                Memory.objects.bulk_create(rows)
                Binder.objects.get(pk=1).delete()

                messages.success(request, (f"{count} entries saved"))
                return redirect("upload_memories")

        return render(request, "upload_memories.html", {})


@staff_member_required
def display_memories(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["action_on_memories"] == "filter":
                client = request.POST["client"]

                memories = KnowledgeManager().display_memories_by_client(client)

                return render(request, "display_memories.html", {
                    "clients": clients,
                    "memories": memories
                    })

        return render(request, "display_memories.html", {
            "clients": clients
            })


@staff_member_required
def display_memory(request, unique_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        memory = KnowledgeManager().display_memory(unique_id)

        if request.method == "POST":
            if request.POST["action_on_memories"] == "remove":

                KnowledgeManager().remove_memory(unique_id)

                return redirect("display_memories")

        return render(request, "display_memory.html", {
            "memory": memory
            })


@staff_member_required
def upload_pronunciation(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["actoion_on_upload"] == "upload":
                instance = Binder(binder=request.FILES["csv_file"], id=1)
                instance.save()

                messages.success(request, ("File uploaded"))
                return render(request, "upload_pronunciation.html", {})

            elif request.POST["actoion_on_upload"] == "save":
                rows = []

                file = Binder.objects.get(pk=1)
                with open(file.binder.path, "rb") as file:
                    file_converted = file.read().decode("utf8", errors="ignore")
                    entries = StringToCsv().convert(file_converted)
                    count = len(entries)

                    now_number = TimeMachine().now_number()
                    today_number = TimeMachine().today_number()

                    for entry in entries:
                        check = Pronunciation.objects.filter(
                                name=entry[1],
                                entry=entry[2]
                                ).exists()

                        if not check:

                            new_row = Pronunciation(
                                publication_stamp=now_number,
                                publication_date=entry[0],
                                name=entry[1],
                                entry=entry[2],
                                due_date=today_number,
                                number_of_reviews=0,
                                answers="",
                                revision_days=""
                                )

                            rows.append(new_row)

                Pronunciation.objects.bulk_create(rows)
                Binder.objects.get(pk=1).delete()

                messages.success(request, (f"{count} entries added"))
                return redirect("upload_pronunciation")

        return render(request, "upload_pronunciation.html", {})


@staff_member_required
def stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["stream_action"] == "filter":
                start = request.POST["start"]
                end = request.POST["end"]

                rows = StreamManager().display_stream_range(start, end)

                return render(request, "stream.html", {
                    "rows": rows
                    })

            elif request.POST["stream_action"] == "delete":
                unique_id = request.POST["unique_id"]

                StreamManager().delete_from_stream(unique_id)

                return redirect("stream")

            elif request.POST["stream_action"] == "explore":
                unique_id = request.POST["unique_id"]

                row = StreamManager().display_stream_entry(unique_id)

                return render(request, "stream_entry.html", {
                    "row": row
                    })

        return render(request, "stream.html", {})


@staff_member_required
def add_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        commands = KnowledgeManager().display_prompts("stream")

        if request.method == "POST":
            client = request.POST["client"]
            date = request.POST["date"]
            command = request.POST["command"]
            value = request.POST["value"]

            date_number = TimeMachine().date_to_number(date)

            StreamManager().add_to_stream_with_date(
                client,
                command,
                value,
                current_user,
                date_number
                )

            return redirect("add_stream")

        return render(request, "add_stream.html", {
            "clients": clients,
            "commands": commands
            })


@staff_member_required
def remove_from_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            client = request.POST["client"]
            stamp = request.POST["stamp"]

            StreamManager().remove_from_stream(
                client,
                stamp
                )

            return redirect("remove_from_stream")

        return render(request, "remove_from_stream.html", {
            "clients": clients
            })


@staff_member_required
def client_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        today = TimeMachine().today()
        month_ago = TimeMachine().month_ago()
        current_client = CurrentClientsManager().current_client(current_user)
        rows = StreamManager().display_stream_range_per_client(
                month_ago,
                today,
                current_client
                )

        return render(request, "client_stream.html", {
            "rows": rows
            })


@staff_member_required
def upload_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_upload"] == "upload":
                instance = Binder(binder=request.FILES["csv_file"], id=1)
                instance.save()

                messages.success(request, ("The file has been uploaded!"))
                return redirect("upload_stream")

            elif request.POST["action_on_upload"] == "save":
                rows = []

                file = Binder.objects.get(pk=1)
                with open(file.binder.path, "rb") as file:
                    file_converted = file.read().decode(
                            "utf8",
                            errors="ignore"
                            )

                    entries = StringToCsv().convert(file_converted)
                    count = len(entries)

                    for entry in entries:
                        new_row = Stream(
                            stamp=entry[0],
                            date_number=entry[1],
                            date=entry[2],
                            name=entry[3],
                            command=entry[4],
                            value=Cleaner().clean_quotation_marks(entry[5]),
                            stream_user=entry[6],
                            status="active"
                            )

                        rows.append(new_row)

                new_entries = Stream.objects.bulk_create(rows)
                Binder.objects.get(pk=1).delete()

                messages.success(request, (f"{count} entries added"))
                return redirect("upload_stream")

        return render(request, "upload_stream.html", {})


@staff_member_required
def agenda(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        commands = KnowledgeManager().display_prompts("stream")

        if request.method == "POST":
            command = request.POST["command"]
            value = request.POST["value"]

            add_to_stream = StreamManager().add_to_stream(
                current_client,
                command,
                value,
                current_user
                )

            return render(request, "agenda.html", {
                "current_client": current_client,
                "commands": commands
                })

        return render(request, "agenda.html", {
            "current_client": current_client,
            "commands": commands
            })


@staff_member_required
def check_homework(request, current_user=''):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        overdue_assignments = CurriculumManager().display_overdue_assignments(current_client)
        uncompleted_assignments = CurriculumManager().display_uncompleted_assignments(current_client)
        completed_assignments = CurriculumManager().display_completed_assignments(current_client)

        if request.method == "POST":
            if request.POST["action_on_check"] == "check":
                item = request.POST["item"]

                output = HomeworkManager().check_assignment(
                        item,
                        current_user
                        )

                messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )

                messages.success(request, ("Marked as completed"))
                return redirect("check_homework")

            elif request.POST["action_on_check"] == "uncheck":
                item = request.POST["item"]
                CurriculumManager().change_status_to_fake_completed(
                        item,
                        current_user
                        )

                messages.success(request, ("Marked as uncompleted"))
                return redirect("check_homework")

            elif request.POST["action_on_check"] == "remove":
                item = request.POST["item"]

                CurriculumManager().remove_curriculum(item)

                messages.success(request, ("Removed"))
                return redirect("check_homework")

        return render(request, "check_homework.html", {
                "overdue_assignments": overdue_assignments,
                "uncompleted_assignments": uncompleted_assignments,
                "completed_assignments": completed_assignments,
                "current_client": current_client
                })


'''
Sentence translation section
'''


@staff_member_required
def upload_sentence_stock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                upload_sentence_stock = SentenceManager().upload_sentence_stock(
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3],
                    )

            messages.success(request, ("The file has been uploaded!"))
            return redirect("upload_sentence_stock")

        return render(request, "upload_sentence_stock.html", {})


@staff_member_required
def sentence_stock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        sentences = SentenceManager().display_sentence_stock()

        return render(request, "sentence_stock.html", {
            "sentences": sentences
            })


@staff_member_required
def update_sentence_stock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        sentences = SentenceManager().display_sentence_stock()
        rows = SentenceManager().display_sentence_stock_json()

        if request.method == "POST":
            if request.POST["action_on_sentence_stock"] == "update":
                sentence_id = request.POST["sentence_id"]
                polish = request.POST["polish"]
                english = request.POST["english"]
                glossary = request.POST["glossary"]

                SentenceManager().update_sentence_stock(
                    sentence_id,
                    polish,
                    english,
                    glossary
                    )

                messages.success(request, ("Sentence updated!"))
                return redirect("update_sentence_stock")    

        return render(request, "update_sentence_stock.html", {
            "sentences": sentences,
            "rows": rows
            })


@staff_member_required
def add_to_sentence_stock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        next_sentence_id = SentenceManager().display_next_sentence_id()

        if request.method == "POST":
            if request.POST["action_on_sentence_stock"] == "add":
                sentence_id = request.POST["sentence_id"]
                polish = request.POST["polish"]
                english = request.POST["english"]
                glossary = request.POST["glossary"]

                SentenceManager().upload_sentence_stock(
                    sentence_id,
                    polish,
                    english,
                    glossary
                    )

                messages.success(request, ("Sentence added!"))
                return redirect("add_to_sentence_stock")

        return render(request, "add_to_sentence_stock.html", {
            "next_sentence_id": next_sentence_id
            })


@staff_member_required
def choose_set_type(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_set"] == "choose":
                set_type = request.POST["set_type"]

                return redirect("compose_set", set_type=set_type)

        return render(request, "choose_set_type.html", {})


@staff_member_required
def compose_set(request, set_type):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        sentences = SentenceManager().display_sentence_stock()
        next_set_id = SentenceManager().display_next_set_id()

        if request.method == "POST":
            if request.POST["action_on_set"] == "compose":
                set_id = request.POST["set_id"]
                set_type = request.POST["set_type"]
                set_name = request.POST["set_name"]
                sentence_1 = request.POST["sentence_1"]
                sentence_2 = request.POST["sentence_2"]
                sentence_3 = request.POST["sentence_3"]
                sentence_4 = request.POST["sentence_4"]
                sentence_5 = request.POST["sentence_5"]
                sentence_6 = request.POST["sentence_6"]
                sentence_7 = request.POST["sentence_7"]
                sentence_8 = request.POST["sentence_8"]
                sentence_9 = request.POST["sentence_9"]
                sentence_10 = request.POST["sentence_10"]

                sentence_ids_list = []
                sentence_ids_list.append(sentence_1)
                sentence_ids_list.append(sentence_2)
                sentence_ids_list.append(sentence_3)
                sentence_ids_list.append(sentence_4)
                sentence_ids_list.append(sentence_5)
                sentence_ids_list.append(sentence_6)
                sentence_ids_list.append(sentence_7)
                sentence_ids_list.append(sentence_8)
                sentence_ids_list.append(sentence_9)
                sentence_ids_list.append(sentence_10)

                sentence_ids = ",".join(sentence_ids_list)

                SentenceManager().add_set(
                    set_id,
                    set_name,
                    sentence_ids,
                    set_type
                    )

                messages.success(request, ("Set created!"))
                return redirect("display_sets")

            elif request.POST["action_on_set"] == "compose_text":
                set_id = request.POST["set_id"]
                set_name = request.POST["set_name"]
                sentence_ids = request.POST["sentence_ids"]

                SentenceManager().add_set(
                    set_id,
                    set_name,
                    sentence_ids,
                    set_type
                    )

                messages.success(request, ("Set created!"))
                return redirect("choose_set_type")

        if set_type == "translation":
            return render(request, "compose_translation_set.html", {
                "set_type": set_type,
                "sentences": sentences,
                "next_set_id": next_set_id
                })
        else:
            return render(request, "compose_set.html", {
                    "set_type": set_type,
                    "sentences": sentences,
                    "next_set_id": next_set_id
                    })


@staff_member_required
def display_sets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        items = SentenceManager().display_all_sets()

        if request.method == "POST":
            if request.POST["action_on_set"] == "compose":

                return redirect("display_sets")

        return render(request, "display_sets.html", {
            "items": items
            })


@staff_member_required
def display_set(request, set_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        set_details = SentenceManager().display_set(set_id)
        sentence_ids = set_details[2]
        sentences = SentenceManager().display_sentences_by_id(sentence_ids)

        return render(request, "display_set.html", {
            "set_id": set_id,
            "set_details": set_details,
            "sentences": sentences
            })


@staff_member_required
def composer(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_clients = ClientsManager().list_current_clients()
        set_names = SentenceManager().display_set_names()

        if request.method == "POST":
            if request.POST["composer_action"] == "compose":
                name = request.POST["name"]
                set_name = request.POST["set_name"]

                sentences = SentenceManager().compose_sentence_lists(name, set_name)

                messages.success(request, (f"{set_name.capitalize()} added to {name}'s sentences!"))
                return render(request, "composer.html", {
                    "set_names": set_names,
                    "current_clients": current_clients,
                    "sentences": sentences
                    })

        return render(request, "composer.html", {
            "set_names": set_names,
            "current_clients": current_clients
            })


@staff_member_required
def composed_sentences(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["search"] == "sentences":
                name = request.POST["name"]
                search_type = request.POST["search"]
                entries = SentenceManager().display_planned_sentences_per_student(name)

                return render(request, "composed_sentences.html", {
                    "current_clients": current_clients,
                    "entries": entries,
                    "search_type": search_type
                    })
            else:
                search_type = request.POST["search"]
                name = request.POST["name"]
                entries = SentenceManager().display_planned_sentence_lists_per_student(name)

                return render(request, "composed_sentences.html", {
                    "current_clients": current_clients,
                    "entries": entries,
                    "search_type": search_type
                    })

        return render(request, "composed_sentences.html", {
            "current_clients": current_clients
            })


@staff_member_required
def grade_sentences(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = SentenceManager().display_sentences_to_grade()
        counter = SentenceManager().count_sentences_to_grade()

        if request.method == "POST":
            sentence_number = request.POST["sentence_number"]
            result = request.POST["result"]

            SentenceManager().grade_sentence_manually(
                    sentence_number,
                    result,
                    current_user
                    )

            return redirect("grade_sentences")

        return render(request, "grade_sentences.html", {
            "entry": entry,
            "counter": counter
            })


@staff_member_required
def label_sentences(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entry = SentenceManager().display_sentences_to_label()
        counter = SentenceManager().count_sentences_to_label()

        if request.method == "POST":
            sentence_number = request.POST["sentence_number"]
            result = request.POST["result"]

            SentenceManager().grade_sentence_manually(
                    sentence_number,
                    result,
                    current_user
                    )

            return redirect("label_sentences")

        return render(request, "label_sentences.html", {
            "entry": entry,
            "counter": counter
            })


'''
Reading section
'''


@staff_member_required
def library(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        positions = BackOfficeManager().display_library()
        next_postion_number = BackOfficeManager().next_postion_number()

        if request.method == "POST":
            if request.POST["library_action"] == "add":
                position_number = request.POST["position_number"]
                title = request.POST["title"]
                wordcount = request.POST["wordcount"]
                link = request.POST["link"]

                BackOfficeManager().add_to_library(
                    position_number,
                    title,
                    wordcount,
                    link
                    )

                return redirect("library")

            else:
                position_number = request.POST["position_number"]

                BackOfficeManager().delete_from_library(
                    position_number,
                    )

                return redirect("library")

        return render(request, "library.html", {
            "positions": positions,
            "next_postion_number": next_postion_number
            })


@staff_member_required
def report_reading(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client = CurrentClientsManager().current_client(current_user)

        if request.method == "POST":
            link = request.POST["link"]

            BackOfficeManager().report_reading(client, link, current_user)

            messages.success(request, ("Reported!"))
            return redirect("report_reading")

        return render(request, "report_reading.html", {})


@staff_member_required
def library_line(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        data = BackOfficeManager().display_reported_library_line()

        if data is None:

            messages.success(request, ("Everything's processed!"))
            return render(request, "library_line.html", {
                "data": data
                })

        link = data[1]
        check_if_in_library = BackOfficeManager().check_if_in_library(link)

        if check_if_in_library is True:
            client = data[0]

            BackOfficeManager().report_reading(client, link, current_user)
            BackOfficeManager().mark_library_line_as_processed(client, link)

            return redirect("library_line")

        if request.method == "POST":
            title = request.POST["title"]
            wordcount = request.POST["wordcount"]
            link = request.POST["link"]
            client = request.POST["client"]

            BackOfficeManager().add_to_library(
                position_number,
                title,
                wordcount,
                link
                )

            BackOfficeManager().report_reading(client, link, current_user)
            BackOfficeManager().mark_library_line_as_processed(client, link)

            return redirect("library_line")

        return render(request, "library_line.html", {
            "data": data
            })


'''
Listening section
'''


@login_required
def report_listening(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client = CurrentClientsManager().current_client(current_user)
        titles = BackOfficeManager().display_titles()
        today_number = TimeMachine().today_number()

        if request.method == "POST":
            title = request.POST["title"]
            number_of_episodes = request.POST["number_of_episodes"]

            # Stream
            BackOfficeManager().report_listening(
                client,
                title,
                number_of_episodes,
                current_user,
                today_number
                )

            return redirect("report_listening")

        return render(request, "report_listening.html", {
            "titles": titles
            })


@staff_member_required
def repertoire(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        titles = BackOfficeManager().display_repertoire()

        if request.method == "POST":
            if request.POST["repertoire_action"] == "add":
                title = request.POST["title"]
                duration = request.POST["duration"]
                title_type = request.POST["title_type"]

                BackOfficeManager().add_to_repertoire(
                    title,
                    duration,
                    title_type
                    )

                return redirect("repertoire")

            elif request.POST["repertoire_action"] == "delete":
                title = request.POST["title"]

                BackOfficeManager().delete_from_repertoire(
                    title
                    )

                return redirect("repertoire")

        return render(request, "repertoire.html", {
            "titles": titles
            })


@staff_member_required
def repertoire_line(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        position = BackOfficeManager().display_reported_repertoire_line()
        counter = BackOfficeManager().count_reported_repertoire_line()

        if request.method == "POST":
            if request.POST["repertoire_line_action"] == "add":
                date_number = request.POST["date_number"]
                title = request.POST["title"]
                duration = request.POST["duration"]
                title_type = request.POST["title_type"]

                BackOfficeManager().process_repertoire_line(
                    title,
                    duration,
                    title_type,
                    position,
                    date_number
                    )

                return redirect("repertoire_line")

            elif request.POST["repertoire_line_action"] == "remove":
                stamp = request.POST["stamp"]
                BackOfficeManager().remove_from_repertoire_line(stamp)

                return redirect("repertoire_line")

        if position is None:

            messages.success(request, ("Everything's processed!"))
            return render(request, "repertoire_line.html", {})

        else:
            return render(request, "repertoire_line.html", {
                "position": position,
                "counter": counter
                })


@staff_member_required
def download_assignments(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_download"] == "download":
                start_date = request.POST["start_date"]
                end_date = request.POST["end_date"]

                check_download = SentenceManager().check_sentences_before_download(
                        start_date,
                        end_date
                        )

                if not check_download:
                    output = ("ERROR", "Grade all the sentences")

                    messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )

                    return redirect("download_assignments")

                response = DownloadManager().download_assignments(
                        start_date,
                        end_date
                        )

                return response

        return render(request, "download_assignments.html", {})


@staff_member_required
def add_course(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        courses = RoadmapManager().display_courses_to_plan()
        course_types = KnowledgeManager().display_prompts("course_type")
        assessment_methods = KnowledgeManager().display_prompts("assessment_method")
        assessment_systems = KnowledgeManager().display_prompts("assessment_system")

        if request.method == "POST":
            if request.POST["action_on_course"] == "add":
                course = request.POST["course"]
                course_type = request.POST["course_type"]
                course_description = request.POST["course_description"]
                registration_description = request.POST["registration_description"]
                assessment_description = request.POST["assessment_description"]
                assessment_method = request.POST["assessment_method"]
                link = request.POST["link"]
                reference_system = request.POST["reference_system"]
                threshold = request.POST["threshold"]
                component_id = request.POST["component_id"]

                RoadmapManager().add_course(
                    course,
                    course_type,
                    course_description,
                    registration_description,
                    assessment_description,
                    assessment_method,
                    link,
                    reference_system,
                    threshold,
                    component_id
                    )

                courses = RoadmapManager().list_courses()
                return render(request, "list_courses.html", {
                    "courses": courses,
                    "course_types": course_types,
                    "assessment_methods": assessment_methods,
                    "assessment_systems": assessment_systems
                    })

            if request.POST["action_on_course"] == "update":
                course = request.POST["course"]
                course_type = request.POST["course_type"]
                course_description = request.POST["course_description"]
                registration_description = request.POST["registration_description"]
                assessment_description = request.POST["assessment_description"]
                assessment_method = request.POST["assessment_method"]
                link = request.POST["link"]
                reference_system = request.POST["reference_system"]
                threshold = request.POST["threshold"]
                component_id = request.POST["component_id"]
                course_id = request.POST["course_id"]

                RoadmapManager().update_course(
                    course,
                    course_type,
                    course_description,
                    registration_description,
                    assessment_description,
                    assessment_method,
                    link,
                    reference_system,
                    threshold,
                    component_id,
                    course_id
                    )

                courses = RoadmapManager().list_courses()
                return render(request, "list_courses.html", {
                    "courses": courses,
                    "course_types": course_types,
                    "assessment_methods": assessment_methods,
                    "assessment_systems": assessment_systems
                    })      

        return render(request, "add_course.html", {
            "courses": courses,
            "course_types": course_types,
            "assessment_methods": assessment_methods,
            "assessment_systems": assessment_systems
            })


@staff_member_required
def list_courses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        courses = RoadmapManager().list_courses()
        course_types = KnowledgeManager().display_prompts("course_type")
        assessment_methods = KnowledgeManager().display_prompts("assessment_method")
        assessment_systems = KnowledgeManager().display_prompts("assessment_system")

        if request.method == "POST":
            if request.POST["action_on_course"] == "more":
                course = request.POST["course"]
                course = RoadmapManager().display_course(course)

                return render(request, "display_course.html", {"course": course})

            if request.POST["action_on_course"] == "edit":
                course = request.POST["course"]
                course_id = request.POST["course_id"]
                course = RoadmapManager().display_course(course)

                return render(request, "update_course.html", {
                    "course_id": course_id,
                    "course": course,
                    "course_types": course_types,
                    "assessment_methods": assessment_methods,
                    "assessment_systems": assessment_systems
                    })

            if request.POST["action_on_course"] == "delete":
                course = request.POST["course"]     
                RoadmapManager().delete_course(course)
                RoadmapManager().delete_roadmap_based_on_course(course)
                courses = RoadmapManager().list_courses()

                return render(request, "list_courses.html", {
                    "courses": courses
                    })

        return render(request, "list_courses.html", {"courses": courses})


@staff_member_required
def display_course(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_course"] == "more":
                course = request.POST["course"]
                course = RoadmapManager().display_course(course)

                return render(request, "display_course.html", {"course": course})


@staff_member_required
def add_roadmap(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        names = ClientsManager().list_current_clients()
        courses = RoadmapManager().list_courses()

        if request.method == "POST":
            if request.POST["action_on_roadmap"] == "add":
                client = request.POST["client"]
                semester = request.POST["semester"]
                course = request.POST["course"]
                deadline = request.POST["deadline"]
                item = request.POST["item"]
                status_type = request.POST["status_type"]

                RoadmapManager().add_roadmap(
                    client,
                    semester,
                    course,
                    deadline,
                    current_user,
                    item,
                    status_type
                    )

                return redirect("roadmaps")

        return render(request, "add_roadmap.html", {
            "names": names,
            "courses": courses
            })


@staff_member_required
def update_roadmap(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_roadmap"] == "update":
                client = request.POST["client"]
                semester = request.POST["semester"]
                course = request.POST["course"]
                deadline = request.POST["deadline"]
                item = request.POST["item"]
                status = request.POST["status"]
                status_type = request.POST["status_type"]
                roadmap_id_number = request.POST["roadmap_id_number"] 

                RoadmapManager().update_roadmap_details(
                    client,
                    semester,
                    course,
                    deadline,
                    current_user,
                    item,
                    status,
                    status_type,
                    roadmap_id_number
                    )

                return redirect("roadmaps")


@login_required
def display_roadmap_details(request, course_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        course = RoadmapManager().display_course_by_id(course_id)

        # roadmap_details = RoadmapManager().roadmap_details(roadmap_id_number)
        # course = roadmap_details[2]
        # course_details = RoadmapManager().display_course(course)
        # grades = RoadmapManager().display_grades(current_user, course)
        # assessment_method = course_details[5]
        # result = 0

        if assessment_method == "statistics":
            assessment_system = course_details[7]
            statistics = StreamManager().statistics(current_user)
            result = statistics[assessment_system]

        return render(request, "display_roadmap_details.html", {
            "course": course
            })


@staff_member_required
def add_profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client_names = RoadmapManager().display_profile_names()
        programs = RoadmapManager().display_programs()

        if request.method == "POST":
            if request.POST["action_on_profile"] == "add":
                name = request.POST["client_name"]
                display_name = request.POST["display_name"]
                avatar = request.POST["avatar"]
                current_english_level = request.POST["current_english_level"]
                current_semester = request.POST["current_semester"]
                current_specialization = request.POST["current_specialization"]
                current_degree = request.POST["current_degree"]
                early_admission = request.POST["early_admission"]
                semester_1_status = request.POST["semester_1_status"]
                semester_2_status = request.POST["semester_2_status"]
                semester_3_status = request.POST["semester_3_status"]
                semester_4_status = request.POST["semester_4_status"]
                semester_5_status = request.POST["semester_5_status"]
                semester_6_status = request.POST["semester_6_status"]
                semester_7_status = request.POST["semester_7_status"]
                semester_8_status = request.POST["semester_8_status"]
                semester_9_status = request.POST["semester_9_status"]
                semester_10_status = request.POST["semester_10_status"]
                semester_11_status = request.POST["semester_11_status"]
                semester_12_status = request.POST["semester_12_status"]
                semester_13_status = request.POST["semester_13_status"]
                semester_14_status = request.POST["semester_14_status"]
                semester_15_status = request.POST["semester_15_status"]
                semester_16_status = request.POST["semester_16_status"]
                associates_degree_status = request.POST["associates_degree_status"]
                bachelors_degree_status = request.POST["bachelors_degree_status"]
                masters_degree_status = request.POST["masters_degree_status"]
                doctorate_degree_status = request.POST["doctorate_degree_status"]
                professors_title_status = request.POST["professors_title_status"]
                current_program = request.POST["current_program"]

                RoadmapManager().add_profile(
                    name,
                    display_name,
                    avatar,
                    current_english_level,
                    current_semester,
                    current_specialization,
                    current_degree,
                    early_admission,
                    semester_1_status,
                    semester_2_status,
                    semester_3_status,
                    semester_4_status,
                    semester_5_status,
                    semester_6_status,
                    semester_7_status,
                    semester_8_status,
                    semester_9_status,
                    semester_10_status,
                    semester_11_status,
                    semester_12_status,
                    semester_13_status,
                    semester_14_status,
                    semester_15_status,
                    semester_16_status,
                    associates_degree_status,
                    bachelors_degree_status,
                    masters_degree_status,
                    doctorate_degree_status,
                    professors_title_status,
                    current_program
                    )

                return redirect("profiles")

        return render(request, "add_profile.html", {
            "client_names": client_names,
            "programs": programs
            })


@staff_member_required
def profiles(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profiles = RoadmapManager().display_profiles()

        if request.method == "POST":
            if request.POST["action_on_profile"] == "edit":
                client_name = request.POST["client_name"]

                profile = RoadmapManager().display_profile(client_name)
                programs = RoadmapManager().display_programs()

                return render(request, "update_profile.html", {
                    "profile": profile,
                    "programs": programs
                    })

            if request.POST["action_on_profile"] == "update":
                client_name = request.POST["client_name"]
                display_name = request.POST["display_name"]
                avatar = request.POST["avatar"]
                current_english_level = request.POST["current_english_level"]
                current_semester = request.POST["current_semester"]
                current_specialization = request.POST["current_specialization"]
                current_degree = request.POST["current_degree"]
                early_admission = request.POST["early_admission"]
                semester_1_status = request.POST["semester_1_status"]
                semester_2_status = request.POST["semester_2_status"]
                semester_3_status = request.POST["semester_3_status"]
                semester_4_status = request.POST["semester_4_status"]
                semester_5_status = request.POST["semester_5_status"]
                semester_6_status = request.POST["semester_6_status"]
                semester_7_status = request.POST["semester_7_status"]
                semester_8_status = request.POST["semester_8_status"]
                semester_9_status = request.POST["semester_9_status"]
                semester_10_status = request.POST["semester_10_status"]
                semester_11_status = request.POST["semester_11_status"]
                semester_12_status = request.POST["semester_12_status"]
                semester_13_status = request.POST["semester_13_status"]
                semester_14_status = request.POST["semester_14_status"]
                semester_15_status = request.POST["semester_15_status"]
                semester_16_status = request.POST["semester_16_status"]
                associates_degree_status = request.POST["associates_degree_status"]
                bachelors_degree_status = request.POST["bachelors_degree_status"]
                masters_degree_status = request.POST["masters_degree_status"]
                doctorate_degree_status = request.POST["doctorate_degree_status"]
                professors_title_status = request.POST["professors_title_status"]
                current_program = request.POST["current_program"]

                RoadmapManager().update_profile(
                    client_name,
                    display_name,
                    avatar,
                    current_english_level,
                    current_semester,
                    current_specialization,
                    current_degree,
                    early_admission,
                    semester_1_status,
                    semester_2_status,
                    semester_3_status,
                    semester_4_status,
                    semester_5_status,
                    semester_6_status,
                    semester_7_status,
                    semester_8_status,
                    semester_9_status,
                    semester_10_status,
                    semester_11_status,
                    semester_12_status,
                    semester_13_status,
                    semester_14_status,
                    semester_15_status,
                    semester_16_status,
                    associates_degree_status,
                    bachelors_degree_status,
                    masters_degree_status,
                    doctorate_degree_status,
                    professors_title_status,
                    current_program
                    )

                profiles = RoadmapManager().display_profiles()

                return render(request, "profiles.html", {
                    "profiles": profiles
                    })

        return render(request, "profiles.html", {
            "profiles": profiles
            })


@staff_member_required
def display_profile(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profile = RoadmapManager().display_profile(client)

        return render(request, "display_profile.html", {
            "profile": profile
            })


@staff_member_required
def update_profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profile = RoadmapManager().display_profile()

        return render(request, "update_profile.html", {
            "profile": profile
            })


@staff_member_required
def roadmaps(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client_names = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["action_on_roadmaps"] == "find":
                client_name = request.POST["client_name"]
                semester = request.POST["semester"]

                courses = RoadmapManager().display_roadmap(client_name, semester)

                return render(request, "roadmaps.html", {
                    "client_names": client_names,
                    "courses": courses
                    })

            elif request.POST["action_on_roadmaps"] == "edit":
                roadmap_id_number = request.POST["roadmap_id_number"]
                roadmap_details = RoadmapManager().display_roadmap_details(roadmap_id_number)
                deadline_date = TimeMachine().number_to_system_date(roadmap_details[4])
                names = ClientsManager().list_current_clients()
                courses = RoadmapManager().list_courses()

                return render(request, "update_roadmap.html", {
                    "names": names,
                    "courses": courses,
                    "roadmap_details": roadmap_details,
                    "deadline_date": deadline_date
                    })

            elif request.POST["action_on_roadmaps"] == "remove":
                roadmap_id_number = request.POST["roadmap_id_number"]

                RoadmapManager().remove_roadmap(roadmap_id_number)

                return render(request, "roadmaps.html", {
                    "client_names": client_names
                    })

            elif request.POST["action_on_roadmaps"] == "more":
                roadmap_id_number = request.POST["roadmap_id_number"]
                roadmap_details = RoadmapManager().display_roadmap_details(roadmap_id_number)
                course = roadmap_details[2]
                course_details = RoadmapManager().display_course(course)
                grades = RoadmapManager().display_grades(current_user, course)

                deadline = TimeMachine().number_to_system_date(roadmap_details[4])
                threshold = RoadmapManager().display_course_threshold(course)
                assessment_method = course_details[5]
                assessment_system = course_details[7]
                status_type = roadmap_details[9]
                deadline_number = roadmap_details[4]
                today_number = TimeMachine().today_number()

                if assessment_method == "statistics":
                    statistics = StreamManager().advanced_statistics(current_user)
                    result = statistics[assessment_system]

                elif assessment_method == "assignment":
                    if assessment_system == "item":

                        item = roadmap_details[7]
                        if item == 0:
                            result = "uncompleted"
                        else:
                            result = CurriculumManager().display_assignment_status(item)

                else:
                    if assessment_system == "last_final":
                        result = RoadmapManager().display_last_final_grade(current_user, course)
                    elif assessment_system == "average_final":
                        result = RoadmapManager().display_average_final_grade(current_user, course)
                    elif assessment_system == "last_mid_term":
                        result = RoadmapManager().display_last_midterm_grade(current_user, course)
                    else:
                        result = RoadmapManager().display_average_midterm_grade(current_user, course)

                # Status: passed/ongoing/failed
                if status_type == "manual":
                    status = roadmap_details[6]
                else:
                    if assessment_method == "assignment":

                        if result == "completed":
                            status = "passed"

                        else:
                            if deadline_number > today_number:
                                status = "ongoing"
                            else:
                                status = "failed"

                    elif result >= threshold:
                        status = "passed"

                    elif result == -1:
                        status = "ongoing"

                    elif assessment_method == "statistics" or assessment_system == "average_midterm" or assessment_system == "average_final":

                        if deadline_number > today_number:
                            status = "ongoing"

                        else:
                            status = "failed"

                    else:
                        status = "failed"

                RoadmapManager().update_roadmap(roadmap_id_number, status)
                deadline = TimeMachine().number_to_system_date(roadmap_details[4])

                return render(request, "display_roadmap_details.html", {
                    "roadmap_details": roadmap_details,
                    "course_details": course_details,
                    "deadline": deadline,
                    "grades": grades,
                    "status": status,
                    "assessment_method": assessment_method,
                    "assessment_system": assessment_system,
                    "result": result
                    })

        return render(request, "roadmaps.html", {
            "client_names": client_names
            })


@staff_member_required
def add_material(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_material"] == "add":
                title = request.POST["title"]
                content = request.POST["content"]

                DocumentManager().add_material(title, content)
                materials = DocumentManager().display_materials()

                return render(request, "materials.html", {
                    "materials": materials
                    })

        return render(request, "add_material.html", {})


@login_required
def materials(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        materials = DocumentManager().display_materials()

        if request.method == "POST":
            if request.POST["action_on_material"] == "more":
                title = request.POST["title"]

                material = DocumentManager().display_material(title)

                return render(request, "display_material.html", {
                    "material": material
                    })

        return render(request, "materials.html", {
            "materials": materials
            })


@login_required
def display_material(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_material"] == "delete":
                title = request.POST["title"],

                DocumentManager().delete_material(title)
                materials = DocumentManager().display_materials()

                return render(request, "materials.html", {
                    "materials": materials
                    })

        return render(request, "display_material.html", {})


@login_required
def ranking(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        rows = StreamManager().display_ranking()
        context = {"rows": rows}

        user_agent = get_user_agent(request)
        if user_agent.is_mobile:
            return render(request, "m_ranking.html", context)
        else:
            return render(request, "ranking.html", context)


@login_required
def my_statistics(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        stats = StreamManager().statistics(current_user)
        user_agent = get_user_agent(request)
        context = {"stats": stats}

        if user_agent.is_mobile:
            return render(request, "m_my_statistics.html", context)
        else:
            return render(request, "my_statistics.html", context)


@login_required
def notifications(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "notifications.html", {
            })


@login_required
def announcements(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        announcements = BackOfficeManager().display_announcements()

        if request.method == "POST":
            if request.POST["action_on_announcement"] == "more":
                notification_id = request.POST["notification_id"]

                return redirect("announcement", notification_id=notification_id)

            elif request.POST["action_on_announcement"] == "update":
                notification_id = request.POST["notification_id"]

                return redirect("update_announcement", notification_id=notification_id)

        return render(request, "announcements.html", {
            "announcements": announcements
            })


@staff_member_required
def make_announcement(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_users()

        if request.method == "POST":
            if request.POST["action_on_announcement"] == "publish":
                sender = current_user
                recipients = request.POST.getlist("recipients")
                subject = request.POST["subject"]
                content = request.POST["content"]
                notification_type = request.POST["notification_type"]
                content_type = request.POST["content_type"]
                color = request.POST["color"]
                threshold = request.POST["threshold"]
                status = "sent"

                BackOfficeManager().add_notifications(
                    sender,
                    recipients,
                    subject,
                    content,
                    notification_type,
                    status,
                    content_type,
                    color,
                    threshold
                    )

                return redirect("announcements")

        return render(request, "make_announcement.html", {
            "clients": clients
            })


@staff_member_required
def update_announcement(request, notification_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        announcement = BackOfficeManager().display_announcement(notification_id)

        if request.method == "POST":
            if request.POST["action_on_announcement"] == "update":
                subject = request.POST["subject"]
                content = request.POST["content"]
                notification_type = request.POST["notification_type"]
                status = request.POST["status"]
                content_type = request.POST["content_type"]
                color = request.POST["color"]
                threshold = request.POST["threshold"]

                BackOfficeManager().update_notifications(
                    notification_id,
                    subject,
                    content,
                    notification_type,
                    status,
                    content_type,
                    color,
                    threshold
                    )

                return redirect("announcements")

        return render(request, "update_announcement.html", {
            "notification_id": notification_id,
            "announcement": announcement
            })


@login_required
def announcement(request, notification_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)

        announcement = BackOfficeManager().display_announcement(notification_id)
        stamp = TimeMachine().number_to_system_date_time_clean(announcement[1])
        listing = f"announcement_{notification_id}"
        takers = BackOfficeManager().display_takers(listing)
        is_taker = BackOfficeManager().check_taker(current_user, listing)

        if request.method == "POST":
            if request.POST["action_on_announcement"] == "back":
                return redirect("campus")

            elif request.POST["action_on_announcement"] == "sign_up":
                
                output = BackOfficeManager().add_taker(
                    current_user,
                    listing,
                    announcement[10]
                    )

                messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )
                return redirect("announcement", notification_id=notification_id)

            elif request.POST["action_on_announcement"] == "drop_out":
                
                output = BackOfficeManager().remove_taker(
                    current_user,
                    listing
                    )

                messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )
                return redirect("announcement", notification_id=notification_id)

        context = {
            "notification_id": notification_id,
            "announcement": announcement,
            "stamp": stamp,
            "takers": takers,
            "is_taker": is_taker
        }

        if user_agent.is_mobile:
            return render(request, "m_announcement.html", context)

        else:
            return render(request, "announcement.html", context)


@staff_member_required
def add_grade(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        courses = RoadmapManager().display_current_courses(current_client)
        tests = KnowledgeManager().display_prompts("tests")

        if request.method == "POST":
            student = current_client
            course = request.POST["course"]
            result = request.POST["result"]
            grade_type = request.POST["grade_type"]
            test = request.POST["test"]

            RoadmapManager().add_grade(
                student,
                course,
                result,
                grade_type,
                current_user,
                test
                )

            messages.success(request, ("Grade added"))
            return redirect("add_grade")

        return render(request, "add_grade.html", {
            "courses": courses,
            "tests": tests
            })


@staff_member_required
def results(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        # current_client = CurrentClientsManager().current_client(current_user)
        # grades = RoadmapManager().display_current_grades_by_client(
        #         current_client
        #         )

        # results = RoadmapManager().display_current_results_by_client(
        #         current_client
        #         )

        # activities = ActivityManager().get_points_over_lifetime(current_client)

        # assignments = ActivityManager().get_uncompleted_assignments_list(current_client)

        # flashcards = VocabularyManager().count_study_time_per_day(
        #         current_client,
        #         "vocabulary"
        #         )

        context = {
            # "current_client": current_client,
            # "grades": grades,
            # "results": results,
            # "activities": activities,
            # "assignments": assignments,
            # "flashcards": flashcards
            }

        return render(request, "results.html", context)


@login_required
def grade(request, grade_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        grade = RoadmapManager().display_grade(grade_id)

        if request.method == "POST":
            if request.POST["action_on_grade"] == "remove":

                RoadmapManager().remove_grade(grade_id)

                return redirect("results")

        context = {
            "grade_id": grade_id,
            "grade": grade
            }

        return render(request, "grade.html", context)


@staff_member_required
def add_option(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        commands = KnowledgeManager().display_prompts("options")

        if request.method == "POST":
            command = request.POST["command"]
            value = request.POST["value"]
            author = current_user

            BackOfficeManager().add_option(
                command,
                value,
                author
                )

            return redirect("display_options")

        return render(request, "add_option.html", {
            "commands": commands
            })


@staff_member_required
def display_options(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        options = BackOfficeManager().display_options()

        if request.method == "POST":
            if request.POST["action_on_option"] == "go_to_add":

                return redirect("add_option")

            elif request.POST["action_on_option"] == "delete":
                option_id = request.POST["option_id"]

                BackOfficeManager().remove_option(option_id)

                return redirect("display_options")

        return render(request, "display_options.html", {
            "options": options
            })


@staff_member_required
def add_question(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_question"] == "add":
                description = request.POST["description"]
                question = request.POST["question"]
                answer_a = request.POST["answer_a"]
                answer_b = request.POST["answer_b"]
                answer_c = request.POST["answer_c"]
                answer_d = request.POST["answer_d"]
                correct_answer = request.POST["correct_answer"]
                question_type = request.POST["question_type"]

                QuizManager().add_question(
                    description,
                    question,
                    answer_a,
                    answer_b,
                    answer_c,
                    answer_d,
                    correct_answer,
                    question_type
                    )

                return redirect("add_question")

        return render(request, "add_question.html", {
            })


@staff_member_required
def display_questions(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        questions = QuizManager().display_questions()

        if request.method == "POST":
            if request.POST["action_on_question"] == "more":
                question_id = request.POST["question_id"]

                question = QuizManager().display_question(question_id)

                return render(request, "update_question.html", {
                    "question": question
                    })

            elif request.POST["action_on_question"] == "update":
                description = request.POST["description"]
                question = request.POST["question"]
                answer_a = request.POST["answer_a"]
                answer_b = request.POST["answer_b"]
                answer_c = request.POST["answer_c"]
                answer_d = request.POST["answer_d"]
                correct_answer = request.POST["correct_answer"]
                question_type = request.POST["question_type"]
                question_id = request.POST["question_id"]

                QuizManager().update_question(
                    description,
                    question,
                    answer_a,
                    answer_b,
                    answer_c,
                    answer_d,
                    correct_answer,
                    question_type,
                    question_id
                    )

                return redirect("display_questions")

        return render(request, "display_questions.html", {
            "questions": questions
            })


@staff_member_required
def add_collection(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        next_collection_id = QuizManager().display_next_collection_id()
        collection_ids = QuizManager().display_collection_ids()
        questions = QuizManager().display_questions()

        if request.method == "POST":
            if request.POST["action_on_collection"] == "update":
                collection_name = request.POST["collection_name"]
                collection_id = request.POST["collection_id"]
                question_id = request.POST["question_id"]

                QuizManager().add_collection(
                    collection_name,
                    collection_id,
                    question_id
                    )

            next_collection_id = QuizManager().display_next_collection_id()

            messages.success(request, ("Collection updated!"))
            return redirect("add_collection")

        return render(request, "add_collection.html", {
            "next_collection_id": next_collection_id,
            "collection_ids": collection_ids,
            "questions": questions
            })


@staff_member_required
def display_collection(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        collection_ids = QuizManager().display_collection_ids()

        if request.method == "POST":
            if request.POST["action_on_collection"] == "search":
                collection_id = request.POST["collection_id"]

                questions = QuizManager().display_collection(collection_id)

                return render(request, "display_collection.html", {
                    "collection_ids": collection_ids,
                    "questions": questions
                    })

            elif request.POST["action_on_collection"] == "remove":
                position_id = request.POST["position_id"]

                QuizManager().remove_from_collection(position_id)

                return redirect("display_collection")

        return render(request, "display_collection.html", {
            "collection_ids": collection_ids,
            })


@staff_member_required
def display_quizzes(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_users()

        if request.method == "POST":
            if request.POST["action_on_quiz"] == "filter":
                client = request.POST["client"]

                quiz_ids = KnowledgeManager().display_quiz_ids_per_client(client)

                return render(request, "display_quizzes_2.html", {
                    "client": client,
                    "quiz_ids": quiz_ids
                    })

            elif request.POST["action_on_quiz"] == "search":
                client = request.POST["client"]
                quiz_id = request.POST["quiz_id"]

                questions = KnowledgeManager().display_quizzes(client, quiz_id)
                quiz = KnowledgeManager().display_quiz_status(quiz_id)

                return render(request, "display_quizzes_3.html", {
                    "questions": questions,
                    "quiz": quiz
                    })

        return render(request, "display_quizzes.html", {
            "clients": clients,
            })


@login_required
def take_quiz(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        quiz_id = QuizManager().find_quiz_id_by_item(item)
        quiz_question_id = QuizManager().display_next_generated_question(quiz_id)
        quiz = QuizManager().display_quiz(quiz_question_id)

        number_of_questions = QuizManager().display_number_of_questions(quiz_id)

        if number_of_questions == 0 or quiz_question_id == 0:
            CurriculumManager().change_status_to_completed(item, current_user)
            QuizManager().update_quiz_status(quiz_id, "completed")
            messages.success(request, ("You've completed the quiz!"))

        try:
            question_id = quiz[1]
            question_type = KnowledgeManager().display_question_type(question_id)
        except Exception as e:
            question_type = ""

        if request.method == "POST":
            if request.POST["answer"] == "ok":
                quiz_id = request.POST["quiz_id"]
                quiz_question_id = request.POST["quiz_question_id"]
                item = request.POST["item"]

                next_quiz_question_id = int(quiz_question_id) + 1

                # Tick off the task in student's to-do list
                number_of_questions = QuizManager().display_number_of_questions(quiz_id)
                if number_of_questions == 0:
                    result = QuizManager().display_result(quiz_id)
                    CurriculumManager().change_status_to_completed(item, current_user)
                    QuizManager().update_quiz_status(quiz_id, "completed")

                    return render(request, "take_quiz_3.html", {
                        "quiz_question_id": quiz_question_id,
                        "item": item,
                        "result": result
                        })

                else:
                    return redirect("take_quiz", item=item)

            elif request.POST["answer"] == "leave":

                page = SubmissionManager().find_landing_page(item)

                if page[0] == "applause":

                    return redirect("applause", activity_points=page[1])
                else:
                    return redirect("campus")

            else:
                answer_raw = request.POST["answer"]
                correct_answer = request.POST["correct_answer"]
                question_id = request.POST["question_id"]

                answer = Cleaner().clean_quotation_marks(answer_raw)

                if answer == correct_answer:
                    result = "correct"
                else:
                    result = "incorrect"

                QuizManager().record_answer(
                    quiz_id,
                    question_id,
                    current_user,
                    answer,
                    result
                    )

                return render(request, "take_quiz_2.html", {
                    "quiz_question_id": quiz_question_id,
                    "quiz_id": quiz_id,
                    "item": item,
                    "quiz": quiz,
                    "number_of_questions": number_of_questions,
                    "answer": answer,
                    "correct_answer": correct_answer,
                    "question_type": question_type
                    })

        return render(request, "take_quiz.html", {
            "quiz_question_id": quiz_question_id,
            "item": item,
            "quiz": quiz,
            "number_of_questions": number_of_questions,
            "question_type": question_type
            })


@staff_member_required
def add_spin(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        next_story = RoadmapManager().display_next_story_number()
        stories = RoadmapManager().display_story_numbers()

        if request.method == "POST":
            if request.POST["action_on_spin"] == "create":
                message = request.POST["message"]
                option_a_text = request.POST["option_a_text"]
                option_b_text = request.POST["option_b_text"]
                option_c_text = request.POST["option_c_text"]
                option_d_text = request.POST["option_d_text"]
                option_a_view = request.POST["option_a_view"]
                option_b_view = request.POST["option_b_view"]
                option_c_view = request.POST["option_c_view"]
                option_d_view = request.POST["option_d_view"]
                option_key = request.POST["option_key"]
                option_a_value = request.POST["option_a_value"]
                option_b_value = request.POST["option_b_value"]
                option_c_value = request.POST["option_c_value"]
                option_d_value = request.POST["option_d_value"]
                view_type = request.POST["view_type"]
                story = request.POST["story"]

                scene = RoadmapManager().display_next_scene_number(story)

                RoadmapManager().add_spin(
                    scene,
                    message,
                    option_a_text,
                    option_b_text,
                    option_c_text,
                    option_d_text,
                    option_a_view,
                    option_b_view,
                    option_c_view,
                    option_d_view,
                    option_key,
                    option_a_value,
                    option_b_value,
                    option_c_value,
                    option_d_value,
                    view_type,
                    story
                    )

                return redirect("add_spin")

        return render(request, "add_spin.html", {
            "next_story": next_story,
            "stories": stories
            })


@staff_member_required
def update_spin(request, scene):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        item = RoadmapManager().display_scene(scene)

        if request.method == "POST":
            if request.POST["action_on_spin"] == "update":
                scene = request.POST["scene"]
                message = request.POST["message"]
                option_a_text = request.POST["option_a_text"]
                option_b_text = request.POST["option_b_text"]
                option_c_text = request.POST["option_c_text"]
                option_d_text = request.POST["option_d_text"]
                option_a_view = request.POST["option_a_view"]
                option_b_view = request.POST["option_b_view"]
                option_c_view = request.POST["option_c_view"]
                option_d_view = request.POST["option_d_view"]
                option_key = request.POST["option_key"]
                option_a_value = request.POST["option_a_value"]
                option_b_value = request.POST["option_b_value"]
                option_c_value = request.POST["option_c_value"]
                option_d_value = request.POST["option_d_value"]
                view_type = request.POST["view_type"]
                story = request.POST["story"]

                RoadmapManager().update_spin(
                    scene,
                    message,
                    option_a_text,
                    option_b_text,
                    option_c_text,
                    option_d_text,
                    option_a_view,
                    option_b_view,
                    option_c_view,
                    option_d_view,
                    option_key,
                    option_a_value,
                    option_b_value,
                    option_c_value,
                    option_d_value,
                    view_type,
                    story
                    )

                return redirect("display_story")

        return render(request, "update_spin.html", {
            "item": item,
            "scene": scene
            })


@login_required
def display_spin(request, client, story, scene=1, watchword=0):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        item = RoadmapManager().display_next_scene(story, scene)
        message = item[0].replace("<<first_name>>", first_name.capitalize())
        message = message.replace("<<last_name>>", last_name.capitalize())

        if watchword == 0:
            watchword = random.randint(1000000000000, 9999999999999)

        if request.method == "POST":
            view_type = request.POST["view_type"]
            data = request.POST["response"]
            cue = request.POST["option_key"]
            watchword = request.POST["watchword"]

            rows = data.split(", ")
            response = tuple(rows)
            scene = response[0]
            response = response[1]

            if cue:
                BackOfficeManager().add_to_store(
                    watchword,
                    cue,
                    response
                    )

            if view_type == "last_view":

                items = BackOfficeManager().display_from_store(watchword)
                semester = items["semester"][0]
                course_ids_list = items["courses"]

                course_ids = tuple(course_ids_list)
                courses = RoadmapManager().display_courses_by_ids(course_ids)

                CurriculumPlanner().plan_courses(
                    current_user,
                    current_user,
                    semester,
                    course_ids_list
                    )

                BackOfficeManager().reset_store(watchword)
                StreamManager().add_to_stream(
                    current_user,
                    "Covered story",
                    story,
                    current_user
                    )

                messages.success(request, ("Congratulations!"))
                return redirect("profile")

            else:
                return redirect(
                    "display_spin",
                    client=client,
                    story=story,
                    scene=scene,
                    watchword=watchword
                    )

        return render(request, "display_spin.html", {
            "client": client,
            "story": story,
            "item": item,
            "message": message,
            "watchword": watchword
            })


@staff_member_required
def display_story(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        stories = RoadmapManager().display_story_numbers()

        if request.method == "POST":
            if request.POST["action_on_story"] == "filter":
                story = request.POST["story"]

                items = RoadmapManager().display_story(story)

                return render(request, "display_story.html", {
                    "stories": stories,
                    "items": items
                    })

            elif request.POST["action_on_story"] == "explore":
                scene = request.POST["scene"]

                return redirect("update_spin", scene=scene)

        return render(request, "display_story.html", {
            "stories": stories
            })


@login_required
def rules(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        rules = BackOfficeManager().display_rules()

        return render(request, "rules.html", {
            "rules": rules
            })


@staff_member_required
def add_program(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_program"] == "add":
                program_name = request.POST["program_name"]
                degree = request.POST["degree"]
                description = request.POST["description"]
                courses = request.POST["courses"]
                image = request.POST["image"]

                RoadmapManager().add_program(
                    program_name,
                    degree,
                    description,
                    courses,
                    image
                    )

                messages.success(request, ("Program added!"))
                return redirect("programs")

        return render(request, "add_program.html", {})


@staff_member_required
def update_program(request, program_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        program = RoadmapManager().display_program(program_id)

        if request.method == "POST":
            if request.POST["action_on_program"] == "update":
                program_name = request.POST["program_name"]
                degree = request.POST["degree"]
                description = request.POST["description"]
                courses = request.POST["courses"]
                image = request.POST["image"]

                RoadmapManager().update_program(
                    program_name,
                    degree,
                    description,
                    courses,
                    image,
                    program_id
                    )

                messages.success(request, ("Program updated!"))
                return redirect("programs")

        return render(request, "update_program.html", {
            "program": program,
            "program_id": program_id
            })


@staff_member_required
def manage_programs_and_courses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        courses = RoadmapManager().display_courses()
        programs = RoadmapManager().display_programs()

        if request.method == "POST":
            if request.POST["action"] == "assign_course":
                client = request.POST["client"]
                course = request.POST["course"]
                semester = request.POST["semester"]
                program = "custom"

                output = CurriculumPlanner().assign_course(
                    client,
                    current_user,
                    course,
                    semester,
                    program
                    )

                messages.add_message(
                        request,
                        getattr(messages, output[0]),
                        output[1]
                        )
                return redirect("manage_programs_and_courses")

            if request.POST["action"] == "assign_program":
                client = request.POST["client"]
                program = request.POST["program"]
                semester = request.POST["semester"]

                CurriculumPlanner().assign_program(
                    client,
                    program,
                    semester
                    )

                messages.success(request, ("Program assigned"))
                return redirect("manage_programs_and_courses")

        context = {
            "clients": clients,
            "courses": courses,
            "programs": programs
            }

        return render(request, "manage_programs_and_courses.html", context)


@login_required
def programs(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        programs = RoadmapManager().display_programs()

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_programs.html", {
                "programs": programs
                })
        else:
            return render(request, "programs.html", {
                "programs": programs
                })


@login_required
def program(request, program_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        program = RoadmapManager().display_program(program_id)

        try:
            course_ids = tuple(program[3].split(", "))

            if len(course_ids) == 1:
                course_ids = f"({course_ids[0]})"

            courses = RoadmapManager().display_courses_by_ids(course_ids)

        except Exception as e:
            courses = []

        if request.method == "POST":
            if request.POST["action_on_program"] == "go_to_update":
                program_id = request.POST["program_id"]

                return redirect("update_program", program_id=program_id)

        return render(request, "program.html", {
            "program": program,
            "program_id": program_id,
            "courses": courses
            })


@staff_member_required
def plan_program(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = CurriculumPlanner().client_to_plan_program()
        programs = RoadmapManager().display_programs()
        semesters = RoadmapManager().display_profiles()

        if request.method == "POST":
            if request.POST["action_on_program"] == "plan":
                client = request.POST["client"]
                program_id = request.POST["program_id"]
                semester = request.POST["semester"]

                info = CurriculumPlanner().plan_program(
                    client,
                    current_user,
                    program_id,
                    semester
                    )

                messages.success(request, (f"{info}"))
                return redirect("plan_program")

        return render(request, "plan_program.html", {
            "clients": clients,
            "programs": programs,
            "semesters": semesters
            })


@login_required
def courses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        courses = RoadmapManager().display_courses()

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_courses.html", {
                "courses": courses
                })
        else:
            return render(request, "courses.html", {
                "courses": courses
                })


@login_required
def my_courses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        courses = RoadmapManager().display_current_courses_by_client(
                current_user
                )

        context = {"courses": courses}

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_courses.html", context)
        else:
            return render(request, "my_courses.html", context)


@login_required
def my_grades(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        grades = RoadmapManager().display_current_grades_by_client(
                client
                )

        context = {
            "client": client,
            "grades": grades
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_grades.html", context)
        else:
            return render(request, "my_grades.html", context)


@login_required
def my_final_grades(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        grades = RoadmapManager().display_current_results_by_client(
                client
                )

        context = {
            "client": client,
            "grades": grades
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_final_grades.html", context)
        else:
            return render(request, "my_final_grades.html", context)


@login_required
def my_activity_points(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        today = TimeMachine().today()
        moon = TimeMachine().get_date_from_today(29)

        points = ActivityManager().get_history(
            client,
            moon,
            today
            )

        context = {
            "client": client,
            "points": points
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_activity_points.html", context)
        else:
            return render(request, "my_activity_points.html", context)


@login_required
def my_deadlines(request, client):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        assignments = CurriculumManager().get_assignments_fortnight(
            client
            )

        context = {
            "client": client,
            "assignments": assignments
            }

        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, "m_my_deadlines.html", context)
        else:
            return render(request, "my_deadlines.html", context)


@login_required
def course(request, course_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        course = RoadmapManager().display_course_by_id(course_id)

        return render(request, "course.html", {
            "course": course
            })


@login_required
def add_ticket(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_users()
        staff = User.objects.filter(is_staff=True)

        if request.method == "POST":
            if request.POST["action_on_ticket"] == "submit":
                client = request.POST["client"]
                ticket_type = request.POST["ticket_type"]
                subject = request.POST["subject"]
                description = request.POST["description"]
                assigned_user = request.POST["assigned_user"]
                responsible_user = request.POST["responsible_user"]
                sentiment = request.POST["sentiment"]

                if assigned_user == "-":
                    status = "new"
                else:
                    status = "assigned"

                BackOfficeManager().add_ticket(
                    client,
                    ticket_type,
                    subject,
                    description,
                    assigned_user,
                    responsible_user,
                    status,
                    sentiment,
                    current_user
                    )

                return redirect("display_open_tickets")

        return render(request, "add_ticket.html", {
            "clients": clients,
            "staff": staff
            })


@staff_member_required
def display_open_tickets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        tickets = BackOfficeManager().display_open_tickets()

        return render(request, "display_open_tickets.html", {
            "tickets": tickets
            })


@staff_member_required
def display_closed_tickets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        tickets = BackOfficeManager().display_closed_tickets()

        return render(request, "display_closed_tickets.html", {
            "tickets": tickets
            })


@staff_member_required
def display_ticket(request, ticket_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        ticket = BackOfficeManager().display_ticket(ticket_id)
        staff = User.objects.filter(is_staff=True)

        if request.method == "POST":
            if request.POST["action_on_ticket"] == "assign":
                assigned_user = request.POST["assigned_user"]

                BackOfficeManager().assign_user_to_ticket(ticket_id, assigned_user)
                BackOfficeManager().change_ticket_status(ticket_id, "assigned")

                return redirect("display_ticket", ticket_id=ticket_id)

            elif request.POST["action_on_ticket"] == "solve":

                BackOfficeManager().change_ticket_status(ticket_id, "in_progress")

                return redirect("display_ticket", ticket_id=ticket_id)

            elif request.POST["action_on_ticket"] == "close":
                response = request.POST["response"]

                BackOfficeManager().add_response_to_ticket(ticket_id, response)
                BackOfficeManager().close_ticket(ticket_id)
                BackOfficeManager().change_ticket_status(ticket_id, "closed")

                return redirect("display_closed_tickets")

            elif request.POST["action_on_ticket"] == "reopen":

                BackOfficeManager().assign_user_to_ticket(ticket_id, "-")
                BackOfficeManager().change_ticket_status(ticket_id, "new")

                return redirect("display_ticket", ticket_id=ticket_id)

            elif request.POST["action_on_ticket"] == "comment":
                comment = request.POST["comment"]

                BackOfficeManager().comment_on_ticket(ticket_id, comment)

                return redirect("display_ticket", ticket_id=ticket_id)

        return render(request, "display_ticket.html", {
            "ticket": ticket,
            "staff": staff
            })

# Categories


@staff_member_required
def add_category(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        categories = AuditManager().display_category_names()

        if request.method == "POST":
            if request.POST["action_on_category"] == "add_new_category":
                category_name = request.POST["category_name"]
                category_display_name = request.POST["category_display_name"]
                category_number = request.POST["category_number"]
                category_value = request.POST["category_value"]

                AuditManager().add_category(
                    category_name,
                    category_display_name,
                    category_number,
                    category_value
                    )

                messages.success(request, ("Category addded!"))
                return redirect("display_categories")

            elif request.POST["action_on_category"] == "add_category_display_name":
                category_name = request.POST["category_name"]
                category_display_name = request.POST["category_display_name"]

                AuditManager().add_category_display_name(
                    category_name,
                    category_display_name
                    )

                messages.success(request, ("Category addded!"))
                return redirect("display_categories")

            elif request.POST["action_on_category"] == "upload":
                csv_file = request.FILES["csv_file"]

                file = csv_file.read().decode("utf8")
                entries = StringToCsv().convert(file)

                for entry in entries:
                    AuditManager().add_category(
                        entry[0],
                        entry[1],
                        entry[2],
                        entry[3]
                        )

                messages.success(request, ("Category addded!"))
                return redirect("display_categories")

        return render(request, "add_category.html", {
            "categories": categories
            })


@staff_member_required
def display_categories(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        categories = AuditManager().display_categories()

        return render(request, "display_categories.html", {
            "categories": categories
            }) 

# Clock


@staff_member_required
def clock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        categories = AuditManager().display_categories()
        status = AuditManager().check_if_clocked_in(current_user)

        if request.method == "POST":
            if request.POST["action_on_clock"] == "start":
                category_display_name = request.POST["category_display_name"]
                remarks = request.POST["remarks"]
                tags = ""

                AuditManager().clock_in(
                    category_display_name,
                    remarks,
                    current_user,
                    "automatic",
                    tags
                    )

                return redirect("clock")

            elif request.POST["action_on_clock"] == "stop":
                AuditManager().clock_out(current_user)

                return redirect("clock")

        return render(request, "clock.html", {
            "categories": categories,
            "status": status
            })


@staff_member_required
def manual_clock(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        categories = AuditManager().display_categories()

        if request.method == "POST":
            if request.POST["action_on_manual_clock"] == "add":
                clock_in = request.POST["clock_in"]
                clock_out = request.POST["clock_out"]
                category_display_name = request.POST["category_display_name"]
                remarks = request.POST["remarks"]
                tags = ""

                AuditManager().clock_in_out(
                    clock_in,
                    clock_out,
                    category_display_name,
                    remarks,
                    current_user,
                    "manual",
                    tags
                    )

                return redirect("timesheet")

        return render(request, "manual_clock.html", {
            "categories": categories
            })


@staff_member_required
def timesheet(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        employees = ClientsManager().list_current_staff()
        categories = AuditManager().display_categories()

        if request.method == "POST":
            if request.POST["action_on_timesheet"] == "filter":
                employee = request.POST["employee"]
                category = request.POST["category"]
                start = request.POST["start"]
                end = request.POST["end"]

                entries = AuditManager().display_entries(
                    employee,
                    category,
                    start,
                    end
                    )

                duration = AuditManager().display_total_duration_h_min(entries)

                return render(request, "timesheet_details.html", {
                    "employee": employee,
                    "category": category,
                    "start": start,
                    "end": end,
                    "entries": entries,
                    "current_user": current_user,
                    "employees": employees,
                    "duration": duration
                    })

            elif request.POST["action_on_timesheet"] == "new":
                return redirect("timesheet")

            elif request.POST["action_on_timesheet"] == "download":
                employee = request.POST["employee"]
                category = request.POST["category"]
                start = request.POST["start"]
                end = request.POST["end"]

                entries = AuditManager().display_entries(
                    employee,
                    category,
                    start,
                    end
                    )

                duration = AuditManager().display_total_duration_h_min(entries)

                path = DocumentManager().create_timesheet_pdf(
                    employee,
                    start,
                    end,
                    duration,
                    entries
                    )

                response = DownloadManager().download_document(path)

                return response

            elif request.POST["action_on_timesheet"] == "download_pdf":
                employee = request.POST["employee"]
                category = request.POST["category"]
                start = request.POST["start"]
                end = request.POST["end"]

                entries = AuditManager().display_entries(
                    employee,
                    category,
                    start,
                    end
                    )

                duration = AuditManager().display_total_duration_h_min(entries)

                path = DocumentManager().create_timesheet_pdf(
                    employee,
                    start,
                    end,
                    duration,
                    entries
                    )

                response = DownloadManager().download_pdf(path)

                return response

        return render(request, "timesheet.html", {
            "current_user": current_user,
            "employees": employees,
            "categories": categories
            })


@staff_member_required
def bill(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        employees = ClientsManager().list_current_staff()

        if request.method == "POST":
            if request.POST["action_on_bill"] == "calculate":
                employee = request.POST["employee"]
                start = request.POST["start"]
                end = request.POST["end"]

                entries = AuditManager().count_billable_hours(
                    employee,
                    start,
                    end
                    )

                return render(request, "bill.html", {
                    "entries": entries,
                    "employees": employees
                    })

        return render(request, "bill.html", {
            "employees": employees
            })


@staff_member_required
def update_timesheet(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        employees = ClientsManager().list_current_staff()

        if request.method == "POST":
            if request.POST["action_on_timesheet"] == "remove":
                employee = request.POST["employee"]
                stamp = request.POST["stamp"]

                entries = AuditManager().remove_entry(
                    employee,
                    stamp
                    )

                messages.success(request, ("Entry removed"))
                return redirect("update_timesheet")

        return render(request, "update_timesheet.html", {
            "current_user": current_user,
            "employees": employees
            })


@staff_member_required
def upload_timesheet(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_timesheet"] == "upload":
                csv_file = request.FILES["csv_file"]

                file = csv_file.read().decode("utf8")
                entries = StringToCsv().convert(file)

                for entry in entries:
                    AuditManager().upload_timesheet(
                        entry[0],
                        entry[1],
                        entry[2],
                        entry[3],
                        entry[4],
                        entry[5],
                        entry[6],
                        entry[7],
                        entry[8],
                        entry[9],
                        entry[10],
                        entry[11],
                        entry[12]
                        )

                messages.success(request, ("Category addded!"))
                return redirect("timesheet")

        return render(request, "upload_timesheet.html", {})


@staff_member_required
def onboard_client(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        ActivityManager().calculate_points_this_week("Joe Doe")

        if request.method == "POST":
            client = request.POST["client"]
            matrix = request.POST["matrix"]

            OnboardingManager().onboard_client(client, current_user, matrix)

            messages.success(request, ("Client onboarded!"))
            return redirect("onboard_client")

        return render(request, "onboard_client.html", {
            "clients": clients
            })


@staff_member_required
def weekly_checklist(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        settlement = ActivityManager().check_if_settle_this_week()

        if request.method == "POST":
            if request.POST["action_on_system"] == "settle_last_week":

                ActivityManager().settle_last_week_activity(current_user)

                return redirect("weekly_checklist")

            if request.POST["action_on_system"] == "update_model_sentences":

                product = SentenceManager().update_model_sentences()

                messages.add_message(
                        request,
                        getattr(messages, product[0]),
                        product[1]
                        )
                return redirect("weekly_checklist")

        return render(request, "weekly_checklist.html", {
            "settlement": settlement
            })


@staff_member_required
def examination_mode(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        phrases = VocabularyManager().display_test_cards(
                current_client,
                "vocabulary"
                )

        sentences = VocabularyManager().display_test_cards(
                current_client,
                "sentences"
                )

        memories = KnowledgeManager().display_memories(current_client)
        entries = KnowledgeManager().display_pronunciation(current_client)

        return render(request, "examination_mode.html", {
            "phrases": phrases,
            "sentences": sentences,
            "memories": memories,
            "entries": entries,
            "current_client": current_client
            })


@login_required
def rating(request, client, category, position):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if category == "reading":
            title_raw = BackOfficeManager().find_position_in_library(position)
            title = title_raw[1]
        elif category == "listening":
            title_raw = BackOfficeManager().find_position_in_theater(position)
            title = title_raw[0]

        if request.method == "POST":
            rating = request.POST["action_on_rating"]

            RatingManager().add_rating(
                client,
                category,
                position,
                rating
                )

            messages.success(request, ("Rated!"))
            return redirect("campus")

        return render(request, "rating.html", {
            "client": client,
            "category": category,
            "position": position,
            "title": title
            })


@staff_member_required
def ratings(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        ratings = RatingManager().display_ratings()

        return render(request, "ratings.html", {
            "ratings": ratings
            })


@staff_member_required
def inspection(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()
        dates = CurriculumPlanner().display_expiration_dates(
                clients
                )

        return render(request, "inspection.html", {
            "dates": dates
            })


@staff_member_required
def mychart(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        labels = []
        data = []

        ratings = RatingManager().display_ratings()
        for rating in ratings:
            labels.append(rating[1])
            data.append(rating[3])

        return render(request, "mychart.html", {
            "labels": labels,
            "data": data
            })


@staff_member_required
def add_challenge(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = ChallengeManager().display_matrices()
        modules = CurriculumManager().display_modules()

        if request.method == "POST":
            if request.POST["action_on_challenge"] == "add":
                matrix = request.POST["matrix"]
                step_type = request.POST["step_type"]
                step_number = request.POST["step_number"]
                title = request.POST["title"]
                text = request.POST["text"]
                image = request.POST["image"]
                module = request.POST["module"]

                ChallengeManager().add_challenge(
                    matrix,
                    step_type,
                    step_number,
                    title,
                    text,
                    image,
                    module
                    )

                messages.success(request, ("Challenge added!"))
                return redirect("add_challenge")

        return render(request, "add_challenge.html", {
            "matrices": matrices,
            "modules": modules
            })


@staff_member_required
def display_challenge_matrices(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = ChallengeManager().display_matrices()

        return render(request, "display_challenge_matrices.html", {
            "matrices": matrices
            })


@staff_member_required
def display_challenges(request, matrix_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrix = ChallengeManager().display_matrix_by_id(matrix_id)
        challenges = ChallengeManager().display_challenges(matrix)

        return render(request, "display_challenges.html", {
            "matrix": matrix,
            "challenges": challenges
            })


@staff_member_required
def display_challenge(request, challenge_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        challenge = ChallengeManager().display_challenge(challenge_id)

        if request.method == "POST":
            if request.POST["action_on_challenge"] == "update":

                return redirect("update_challenge", challenge_id=challenge_id)

        return render(request, "display_challenge.html", {
            "challenge": challenge
            })


@staff_member_required
def update_challenge(request, challenge_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        challenge = ChallengeManager().display_challenge(challenge_id)
        matrices = ChallengeManager().display_matrices()
        modules = CurriculumManager().display_modules()

        if request.method == "POST":
            if request.POST["action_on_challenge"] == "update":
                matrix = request.POST["matrix"]
                step_type = request.POST["step_type"]
                step_number = request.POST["step_number"]
                title = request.POST["title"]
                text = request.POST["text"]
                image = request.POST["image"]
                module = request.POST["module"]

                ChallengeManager().update_challenge(
                    matrix,
                    step_type,
                    step_number,
                    title,
                    text,
                    image,
                    module,
                    challenge_id
                    )

                messages.success(request, ("Challenge updated"))
                return redirect("display_challenge", challenge_id=challenge_id)

        return render(request, "update_challenge.html", {
            "challenge": challenge,
            "matrices": matrices,
            "modules": modules
            })


@login_required
def challenges(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        challenges = ChallengeManager().display_planned_challenges(current_user)
        status = ChallengeManager().refresh_process(challenges)
        activity_points = StreamManager().display_activity(current_user)
        target = StreamManager().display_activity_target(current_user)

        if status is True:
            return redirect("campus")

        return render(request, "challenges.html", {
            "challenges": challenges,
            "activity_points": activity_points,
            "target": target
            })


@login_required
def challenge(request, challenge_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        challenge = ChallengeManager().display_planned_challenge(challenge_id)
        activity_points = challenge[17]
        cta = ChallengeManager().find_challenge(challenge)

        if challenge[4] == "completed":
            return redirect("challenges")

        if challenge[9] == "locked":
            return redirect("challenges")

        if request.method == "POST":
            if request.POST["action_on_challenge"] == "back":

                return redirect("challenges")

            elif request.POST["action_on_challenge"] == "complete":

                result = ChallengeManager().complete_challenge(challenge_id)

                return redirect("applause", activity_points=activity_points)

            elif request.POST["action_on_challenge"] == "submit":

                product = HomeworkManager().choose_action(
                        challenge[16],
                        current_user
                        )

                return redirect(
                        product[0],
                        product[1]
                        )

        return render(request, "challenge.html", {
            "challenge_id": challenge_id,
            "challenge": challenge,
            "cta": cta
            })


@login_required
def applause(request, activity_points):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_applause"] == "leave":

                return redirect("challenges")

        return render(request, "applause.html", {
            "activity_points": activity_points,
            "first_name": first_name
            })


@staff_member_required
def display_challenge_sets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        processes = ChallengeManager().display_processes()

        return render(request, "display_challenge_sets.html", {
            "processes": processes
            })


@staff_member_required
def display_challenge_set(request, process_number):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        ChallengeManager().check_if_process_completed(process_number)
        steps = ChallengeManager().display_steps(process_number)

        if request.method == "POST":
            if request.POST["action_on_challenge"] == "remove":

                ChallengeManager().remove_process(process_number)

                messages.success(request, "Process removed")
                return redirect("display_challenge_sets")

        return render(request, "display_challenge_set.html", {
            "process_number": process_number,
            "steps": steps
            })


@staff_member_required
def remove_multiple_from_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        commands = KnowledgeManager().display_prompts("stream")

        if request.method == "POST":
            if request.POST["action_on_stream"] == "remove_multiple":
                date = request.POST["date"]
                command = request.POST["command"]

                StreamManager().delete_multiple_from_stream(date, command)

                messages.success(request, ("Entries removed from stream"))
                return redirect("stream")

        return render(request, "remove_multiple_from_stream.html", {
            "commands": commands,
            })


@login_required
def deans_office(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        if user_agent.is_mobile:
            return render(request, "m_deans_office.html", {})
        else:
            return render(request, "deans_office.html", {})


@login_required
def hall_of_fame(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        rows = StreamManager().display_hall_of_fame()
        conext = {"rows": rows}

        user_agent = get_user_agent(request)
        if user_agent.is_mobile:
            return render(request, "m_hall_of_fame.html", conext)
        else:
            return render(request, "hall_of_fame.html", conext)


# Analytics


@staff_member_required
def analytics(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "analytics.html", {
            "current_user": current_user
            })


@staff_member_required
def analytics_entries_per_student(request, coach):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        rows = AnalyticsManager().count_new_entries_per_student_last_week(
                current_user
                )

        rates = AnalyticsManager().count_entry_rate_per_student(
                current_user
                )

        totals = AnalyticsManager().count_entry_total_per_student(
                current_user
                )

        return render(request, "analytics_entries_per_student.html", {
            "rows": rows,
            "rates": rates,
            "totals": totals
            })


@staff_member_required
def analytics_entries(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        rows = AnalyticsManager().count_all_new_entries_per_student_last_week()
        rates = AnalyticsManager().count_all_entry_rate_per_student()
        totals = AnalyticsManager().count_all_entry_total_per_student()
        unopened_cards = AnalyticsManager().count_unopened_entries_per_student()

        return render(request, "analytics_entries.html", {
            "rows": rows,
            "rates": rates,
            "totals": totals,
            "unopened_cards": unopened_cards
            })


@staff_member_required
def analytics_indicators(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        indicators = SentenceManager().count_ater_and_atess()
        averages = AnalyticsManager().current_average_score_per_coach()

        return render(request, "analytics_indicators.html", {
            "indicators": indicators,
            "averages": averages
            })


@staff_member_required
def analytics_grades(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        activity_start = Option.objects.filter(
                command="activity_start"
                ).values_list(
                "value", flat=True
                )

        activity_stop = Option.objects.filter(
                command="activity_stop"
                ).values_list(
                "value", flat=True
                )

        activity_start = activity_start[0] if activity_start.exists() else None
        activity_stop = activity_stop[0] if activity_stop.exists() else None

        grades = AnalyticsManager().get_grade_range(
            activity_start,
            activity_stop
            )

        return render(request, "analytics_grades.html", {
            "grades": grades
            })


@staff_member_required
def analytics_activity(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        conditions = ActivityManager().get_points_last_week_per_client()

        return render(request, "analytics_activity.html", {
            "conditions": conditions
            })


@staff_member_required
def analytics_timesheet(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        conditions = ActivityManager().get_points_last_week_per_client()

        return render(request, "analytics_activity.html", {
            "conditions": conditions
            })


@staff_member_required
def voice(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        x = SpeechManager().save("hello")
        print(x)

        return render(request, "voice.html", {})


@staff_member_required
def lab(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "lab.html", {})


def footer(request):
    return render(request, "footer.html", {})