from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings as django_settings
from django.core.files.base import ContentFile, File

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

import csv
import re
import json
import os
import requests
from io import BytesIO
from gtts import gTTS
import random
from zipfile import *

from nieszkolni_app.models import *

from django_user_agents.utils import get_user_agent

from django.template import RequestContext

card_opening_time = 0


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

        announcements = BackOfficeManager().display_latest_announcements()
        user_agent = get_user_agent(request)

        if user_agent.is_mobile:
            return render(request, 'm_campus.html', {
                "announcements": announcements
                })
        else:
            return render(request, 'campus.html', {
                "announcements": announcements
                })


@login_required(login_url='login_user.html')
def vocabulary(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        deck = "vocabulary"
        all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

        if len(all_due_entries) == 0:
            VocabularyManager().reset_line(current_user)
            return render(request, 'congratulations.html', {})

        else:
            global card_opening_time

            now_number = TimeMachine().now_number()
            card_opening_time = now_number

            card_id = all_due_entries[0][0]
            polish = all_due_entries[0][1]
            english = all_due_entries[0][2]
            interval = all_due_entries[0][3]
            old_due_today = len(VocabularyManager().display_old_due_entries(current_user, deck))
            new_due_today = len(VocabularyManager().display_new_due_entries(current_user, deck))
            problematic_due_today = len(VocabularyManager().display_problematic_due_entries(current_user, deck))

            if request.method == "POST":
                if request.POST["answer"] == "show":

                    return render(request, 'view_answer.html', {
                        "english": english,
                        "polish": polish,
                        "old_due_today": old_due_today,
                        "new_due_today": new_due_today,
                        "problematic_due_today": problematic_due_today,
                        "deck": deck,
                        "interval": interval
                        })

                elif request.POST["answer"] != "edit":
                    return render(request, 'vocabulary.html', {
                        "polish": polish,
                        "old_due_today": old_due_today,
                        "new_due_today": new_due_today,
                        "problematic_due_today": problematic_due_today,
                        "deck": deck,
                        "interval": interval
                        })
                else:
                    return render(request, "edit_card.html", {
                        "card_id": card_id,
                        "polish": polish,
                        "english": english
                        })

            return render(request, 'vocabulary.html', {
                "polish": polish,
                "old_due_today": old_due_today,
                "new_due_today": new_due_today,
                "problematic_due_today": problematic_due_today,
                "deck": deck,
                "interval": interval
                })


@login_required(login_url='login_user.html')
def sentences(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        deck = "sentences"
        all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

        if len(all_due_entries) == 0:
            VocabularyManager().reset_line(current_user)
            return render(request, 'congratulations.html', {})

        else:
            global card_opening_time

            now_number = TimeMachine().now_number()
            card_opening_time = now_number

            card_id = all_due_entries[0][0]
            polish = all_due_entries[0][1]
            english = all_due_entries[0][2]
            interval = all_due_entries[0][3]
            old_due_today = len(VocabularyManager().display_old_due_entries(current_user, deck))
            new_due_today = len(VocabularyManager().display_new_due_entries(current_user, deck))
            problematic_due_today = len(VocabularyManager().display_problematic_due_entries(current_user, deck))

            if request.method == "POST":
                if request.POST["answer"] == "show":
                    return render(request, 'view_answer.html', {
                        "english": english,
                        "polish": polish,
                        "old_due_today": old_due_today,
                        "new_due_today": new_due_today,
                        "problematic_due_today": problematic_due_today,
                        "deck": deck,
                        "interval": interval
                        })

                elif request.POST["answer"] != "edit":
                    return render(request, 'sentences.html', {
                        "polish": polish,
                        "old_due_today": old_due_today,
                        "new_due_today": new_due_today,
                        "problematic_due_today": problematic_due_today,
                        "deck": deck,
                        "interval": interval
                        })
                else:
                    return render(request, "edit_card.html", {
                        "card_id": card_id,
                        "polish": polish,
                        "english": english
                        })

            return render(request, 'sentences.html', {
                "polish": polish,
                "old_due_today": old_due_today,
                "new_due_today": new_due_today,
                "problematic_due_today": problematic_due_today,
                "deck": deck,
                "interval": interval
                })


@login_required(login_url='login_user.html')
def view_answer(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        # If a button is clicked
        if request.method == "POST":
            if request.POST["answer"] != "play":
                deck = request.POST["deck"]

                all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

                card_id = all_due_entries[0][0]
                polish = all_due_entries[0][1]
                english = all_due_entries[0][2]
                old_due_today = len(VocabularyManager().display_old_due_entries(current_user, deck))
                new_due_today = len(VocabularyManager().display_new_due_entries(current_user, deck))
                problematic_due_today = len(VocabularyManager().display_problematic_due_entries(current_user, deck))
                interval = all_due_entries[0][3]

                if request.POST["answer"] != "edit":
                    answer = request.POST["answer"]
                    VocabularyManager().update_card(card_id, answer, card_opening_time)

                    all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

                    # If there are no more cards to review
                    if len(all_due_entries) == 0:
                        VocabularyManager().reset_line(current_user)
                        return redirect('congratulations.html')

                    else:
                        return redirect(f'{deck}.html')
                else:
                    return render(request, "edit_card.html", {
                        "card_id": card_id,
                        "polish": polish,
                        "english": english
                        })
            else:
                deck = request.POST["deck"]

                all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

                card_id = all_due_entries[0][0]
                polish = all_due_entries[0][1]
                english = all_due_entries[0][2]
                old_due_today = len(VocabularyManager().display_old_due_entries(current_user, deck))
                new_due_today = len(VocabularyManager().display_new_due_entries(current_user, deck))
                problematic_due_today = len(VocabularyManager().display_problematic_due_entries(current_user, deck))
                interval = all_due_entries[0][3]

                english_1 = re.sub(r"\ssb\s", " somebody ", english)
                english_2 = re.sub(r"\ssb$", " somebody", english_1)
                english_3 = re.sub(r"\ssth\s", " something ", english_2)
                english_4 = re.sub(r"\ssth$", " something", english_3)

                tts = gTTS(english_4, lang="en", tld="com")  
                tts.save('recording.mp3')

        # If no button is clicked
        return render(request, 'view_answer.html', {
            "deck": deck,
            "polish": polish,
            "english": english, 
            "old_due_today": old_due_today,
            "new_due_today": new_due_today,
            "problematic_due_today": problematic_due_today,
            "interval": interval})


@login_required
def edit_card(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            card_id = request.POST["card_id"]

            if "change" in request.POST:
                if request.POST["change"] == "edit":
                    polish = request.POST["polish"]
                    english = request.POST["english"]
                    commit_change = VocabularyManager().edit_card(card_id, polish, english)
                    messages.success(request, ("The changes have been made!"))

                    return redirect("vocabulary.html")

                elif request.POST["change"] == "delete":
                    commit_change = VocabularyManager().delete_card(card_id)
                    messages.success(request, ("The card has been deleted!"))

                    return redirect("vocabulary.html")

        return render(request, "edit_card.html", {"card_id": card_id, "polish": polish, "english": english})


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
            messages.success(request, ("You have successfully logged in."))
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
            internal_email_address = request.POST["internal_email_address"]
            first_name_variable = request.POST["first_name"]
            last_name_variable = request.POST["last_name"]
            password = request.POST["password"]
            system_username = first_name_variable.lower() + last_name_variable.lower()
            username = first_name_variable + " " + last_name_variable

            user = authenticate(request, username=system_username, password=password)

            if user is None:
                user = User.objects.create_user(system_username, internal_email_address, password)
                user.first_name = first_name_variable
                user.last_name = last_name_variable

                is_client = ClientsManager().verify_client(username)
                if is_client is False:

                    try:
                        add = ClientsManager().add_client(
                            username,
                            internal_email_address
                            )

                        user.save()

                    except Exception as e:
                        messages.error(request, ("There has been a mistake. Contact the administration team."))
                        return redirect("register_user")

                    messages.success(request, ("The user has been added to the database."))
                    return redirect("list_current_users")

                else:
                    messages.success(request, ("The student already exists."))

            else:
                messages.success(request, ("The user already exists."))

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

                ClientsManager().edit_client(
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
                    maximal_interval_sentences
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

        current_clients = ClientsManager().list_current_users()

        if request.method == "POST":
            if request.POST["action_on_user"] == "more":
                name = request.POST["client"]

                client_details = ClientsManager().load_client(name)
                user_type = client_details[0]
                phone_number = client_details[2]
                contact_email_address = client_details[3]
                internal_email_address = client_details[5]
                meeting_duration = client_details[6]
                price = client_details[7]
                acquisition_channel = client_details[8]
                recommenders = client_details[9]
                reasons_for_resignation = client_details[10]
                status = client_details[11]
                coach = client_details[12]
                level = client_details[13]
                daily_limit_of_new_vocabulary = client_details[14]
                maximal_interval_vocabulary = client_details[15]
                daily_limit_of_new_sentences = client_details[16]
                maximal_interval_sentences = client_details[17]

                return render(request, "register_client.html", {
                    "name": name,
                    "user_type": user_type,
                    "phone_number": phone_number,
                    "contact_email_address": contact_email_address,
                    "internal_email_address": internal_email_address,
                    "meeting_duration": meeting_duration,
                    "price": price,
                    "acquisition_channel": acquisition_channel,
                    "recommenders": recommenders,
                    "reasons_for_resignation": reasons_for_resignation,
                    "status": status,
                    "coach": coach,
                    "level": level,
                    "daily_limit_of_new_vocabulary": daily_limit_of_new_vocabulary,
                    "maximal_interval_vocabulary": maximal_interval_vocabulary,
                    "daily_limit_of_new_sentences": daily_limit_of_new_sentences,
                    "maximal_interval_sentences": maximal_interval_sentences
                    })
            else:

                return render(request, "list_current_users.html", {
                    "current_clients": current_clients
                    })

        return render(request, "list_current_users.html", {
            "current_clients": current_clients
            })


@login_required
def options(request, template_name="404.html"):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client = Client.objects.get(name=current_user)
        daily_limit_of_new__vocabulary = client.daily_limit_of_new_vocabulary
        daily_limit_of_new_sentences = client.daily_limit_of_new_sentences
        maximal_interval_vocabulary = client.maximal_interval_vocabulary
        maximal_interval_sentences = client.maximal_interval_sentences

        if request.method == "POST":
            if request.POST["action_on_client_option"] == "change_vocabulary_limit":
                new_limit = request.POST["daily_limit_of_new_vocabulary"]

                client.daily_limit_of_new_vocabulary = new_limit
                client.save()

                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_sentences_limit":
                new_limit = request.POST["daily_limit_of_new_sentences"]

                client.daily_limit_of_new_sentences = new_limit
                client.save()

                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_vocabulary_interval":
                new_limit = request.POST["maximal_interval_vocabulary"]

                client.maximal_interval_vocabulary = new_limit
                client.save()

                return redirect("options")

            elif request.POST["action_on_client_option"] == "change_sentences_interval":
                new_limit = request.POST["maximal_interval_sentences"]

                client.maximal_interval_sentences = new_limit
                client.save()

                return redirect("options")

        return render(request, "options.html", {
            "daily_limit_of_new_vocabulary": daily_limit_of_new__vocabulary,
            "daily_limit_of_new_sentences": daily_limit_of_new_sentences,
            "maximal_interval_vocabulary": maximal_interval_vocabulary,
            "maximal_interval_sentences": maximal_interval_sentences
            })


@staff_member_required
def staff(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        settlement = ActivityManager().check_if_settle_this_week()

        if request.method == "POST":
            if request.POST["action_on_system"] == "settle_last_week":
                ActivityManager().settle_last_week_activity(current_user)

                return redirect("staff")

        return render(request, "staff.html", {
            "settlement": settlement
            })


@staff_member_required
def old_staff(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "old_staff.html", {})

@staff_member_required
def staff_menu(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "staff_menu.html", {})


@login_required
def profile_menu(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "profile_menu.html", {})


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
def submit_assignment(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["go_to"] == "removal":
                item = request.POST["item"]

                CurriculumManager().remove_curriculum(item)

                return redirect("display_curricula")

            if request.POST["go_to"] == "submission":
                item = request.POST["item"]
                assignment_type = request.POST["assignment_type"]

                return render(request, "submit_assignment_automatically.html", {
                    "item": item,
                    "name": current_user,
                    "assignment_type": assignment_type
                    })

            elif request.POST["go_to"] == "mark_as_read":
                item = request.POST["item"]

                product = HomeworkManager().mark_as_read(
                    item,
                    current_user
                    )

                messages.add_message(request, getattr(messages, product[0]), product[1])
                return redirect("assignments")

            elif request.POST["go_to"] == "mark_as_done":
                item = request.POST["item"]

                product = HomeworkManager().mark_as_done(
                    item,
                    current_user
                    )

                messages.add_message(request, getattr(messages, product[0]), product[1])
                return redirect("assignments")

            elif request.POST["go_to"] == "check_stats":
                command = request.POST["command"]
                item = request.POST["item"]

                product = HomeworkManager().check_stats(
                        item,
                        current_user,
                        command
                        )

                messages.add_message(request, getattr(messages, product[0]), product[1])
                return redirect("assignments")

            elif request.POST["go_to"] == "take_quiz":
                item = request.POST["item"]
                title = request.POST["title"]
                quiz_id = QuizManager().find_quiz_id_by_item(item)
                quiz_question_id = QuizManager().display_next_generated_question(quiz_id)

                return redirect(f"take_quiz/{quiz_question_id}/{item}")

            elif request.POST["go_to"] == "translation":
                item = request.POST["item"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                list_number = SentenceManager().find_list_number_by_item(item)
                sentences = SentenceManager().display_sentence_list(list_number)

                return render(request, "translate_sentences.html", {
                    "item": item,
                    "name": current_user,
                    "assignment_type": assignment_type,
                    "sentences": sentences,
                    "title": title
                    })

            elif request.POST["go_to"] == "translated_sentences":
                item = request.POST["item"]
                name = request.POST["name"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]

                content_raw = []
                translations = []
                for index in range(0, 10):
                    sentence_number = request.POST[f"sentence_number_{index}"]
                    polish = request.POST[f"polish_{index}"]
                    translation = request.POST[f"translation_{index}"]
                    entry = (sentence_number, translation)
                    translations.append(entry)
                    content_raw.append(f"{polish}\n")
                    content_raw.append(f"{translation}\n")

                content = "\n".join(content_raw)

                # Submitting sentence translations
                SentenceManager().submit_sentence_translation(translations)
                SubmissionManager().add_submission(
                    item,
                    name,
                    assignment_type,
                    title,
                    content
                    )

                # Tick off the task in student's to-do list
                CurriculumManager().change_status_to_completed(item, current_user)

                # Add information to stream to count Effort Hours
                StreamManager().add_to_stream(name, "T", 10, current_user)

                messages.success(request, ("Your assignment has been submitted!"))
                return redirect("assignments.html")

            else:
                item = request.POST["item"]
                name = request.POST["client"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                content = request.POST["content"]

                SubmissionManager().add_submission(
                        item,
                        name,
                        assignment_type,
                        title,
                        content
                        )

                # Tick off the task in student's to-do list
                CurriculumManager().change_status_to_completed(item, current_user)

                # Add information to stream to count Effort Hours
                commands = {
                    "essay": "AV",
                    "assignment": "AV",
                    "wordfinder": "WF"
                    }

                wordcount = Wordcounter(content).counter()
                linecount = Wordcounter(content).linecounter()
                command = commands.get(assignment_type)

                if command == "AV":
                    value = wordcount
                else:
                    value = linecount

                StreamManager().add_to_stream(name, command, value, current_user)

                messages.success(request, ("Your assignment has been submitted!"))
                return redirect("assignments.html")
        else:
            return render(request, "submit_assignment.html", {})


@login_required
def list_of_submissions(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        submissions = SubmissionManager().display_students_assignments_limited(current_user)
        tags = BackOfficeManager().display_tags()

        if request.method == "POST":
            unique_id = request.POST["unique_id"]

            submission = SubmissionManager().display_students_assignment(unique_id)
            assignment_type = submission[10]

            if assignment_type != "sentences":

                return render(request, "submission_entry.html", {
                        "submission": submission,
                        "tags": tags
                        })

            else:
                date = submission[0]
                title = submission[1]
                status = submission[9]
                item = submission[11]
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

                return redirect("list_of_assignments_to_grade.html")

        return render(request, "list_of_assignments_to_grade.html", {
            "essays": essays
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
                add_curriculum = CurriculumManager().add_curriculum(
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
            if request.POST["curriculum_action"] == "choose_quiz":
                name = request.POST["name"]        
                names = [name]
                assignment_type = "quiz"

                entries = KnowledgeManager().display_planned_quizzes_per_student(name)

                return render(request, "add_curriculum_2.html", {
                    "client": name,
                    "names": names,
                    "assignment_type": assignment_type,
                    "entries": entries,
                    "modules": modules,
                    "module_status": module_status
                    })

            elif request.POST["curriculum_action"] == "choose_other_modules":
                name = request.POST["name"]
                component_id = request.POST["component_id"]

                module_status = 1
                assignment_type_raw = re.search(r"\w.+_", component_id).group()
                assignment_type = re.sub("_", "", assignment_type_raw)
                names = [name]

                entries = SentenceManager().display_planned_sentence_lists_per_student(name)
                module = CurriculumManager().display_module(component_id)

                return render(request, "add_curriculum_2.html", {
                    "client": name,
                    "names": names,
                    "assignment_type": assignment_type,
                    "entries": entries,
                    "modules": modules,
                    "module": module,
                    "module_status": module_status,
                    "component_id": component_id
                    })

            else:
                item = CurriculumManager().next_item()
                deadline = request.POST["deadline"]
                name = request.POST["name"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                content = request.POST["content"]
                matrix = "custom matrix"
                reference = request.POST["reference"]
                resources = request.POST["resources"]
                conditions = request.POST["conditions"]
                component_id = request.POST["component_id"]

                CurriculumPlanner().plan_curriculum(
                    item,
                    deadline,
                    name,
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


@login_required
def assignments(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        score = ActivityManager().calculate_points_this_week(current_user)


        # Delete
        display_first_name = first_name.capitalize()
        messages.success(request, (f"{display_first_name}, if you encounter an error, take a screenshot and send it to Damian via email."))

        if request.method == "POST":
            item = request.POST["item"]

            return render(request, "assignments.html", {"item": item})

        else:

            uncomplated_assignments = CurriculumManager().display_uncompleted_assignments(current_user)
            complated_assignments = CurriculumManager().display_completed_assignments(current_user)

            if user_agent.is_mobile:
                return render(request, "m_my_to_do_list.html", {
                    "uncomplated_assignments": uncomplated_assignments,
                    "complated_assignments": complated_assignments,
                    "score": score
                    })

            else:
                return render(request, "assignments.html", {
                    "uncomplated_assignments": uncomplated_assignments,
                    "complated_assignments": complated_assignments,
                    "score": score
                    })


@login_required
def assignment(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")

        if request.method == "POST":
            item = request.POST["item"]

            if request.POST["go_to"] == "assignment":

                assignment = CurriculumManager().display_assignment(item)

                if request.POST["go_to"] != "submission":

                    if user_agent.is_mobile:
                        return render(request, "m_assignment.html", {
                                "assignment": assignment,
                                "current_user": current_user,
                                "no_submissions": no_submissions
                                })

                    else:
                        return render(request, "assignment.html", {
                            "assignment": assignment,
                            "current_user": current_user,
                            "no_submissions": no_submissions
                            })

            elif request.POST["go_to"] == "check":

                check = CurriculumManager().change_status_to_completed(
                    item,
                    current_user
                    )

                assignment_type = CurriculumManager().check_assignment_type(item)
                if assignment_type == "reading":

                    position = CurriculumManager().check_position_in_library(item)
                    value = position[2]

                    StreamManager().add_to_stream(
                        current_user,
                        "PV",
                        value,
                        current_user
                        )

                return redirect("check_homework.html")

            elif request.POST["go_to"] == "uncheck":
                uncheck = CurriculumManager().change_status_to_uncompleted(
                    item,
                    current_user
                    )

                return redirect("check_homework.html")


@login_required
def my_pronunciation(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entries = KnowledgeManager().display_pronunciation(current_user)

        return render(request, "my_pronunciation.html", {
            "entries": entries
            })


@staff_member_required
def display_curricula(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["action_on_curriculum"] == "filter":
                name = request.POST["name"]
                assignments = CurriculumManager().display_assignments_for_student(name)

                return render(request, "display_curricula.html", {
                    "clients": clients,
                    "assignments": assignments
                    })

        return render(request, "display_curricula.html", {
            "clients": clients
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
                component == "reading" or
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
            references = SentenceManager().display_sets()
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
            return redirect("display_modules")

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
    return render(request, "coach.html", {})


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
        catalogues = KnowledgeManager().display_catalogues()
        pronunciation = KnowledgeManager().display_all_pronunciation()

        if request.method == "POST":
            last_form = request.POST["add_knowledge"].replace("add_", "")
            if request.POST["add_knowledge"] == "add_pronunciation":
                entry = request.POST["pronunciation_entry"]

                current_client = CurrentClientsManager().current_client(current_user)
                in_pronunciation = KnowledgeManager().check_if_in_pronunciation(current_client, entry)
                if len(in_pronunciation) == 0:

                    add_pronunciation = KnowledgeManager().add_pronunciation(current_client, entry, current_user)

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

                if entry != "0":
                    entry = tuple(entry.split(","))
                    catalogue_title = entry[0]

                    phrases = KnowledgeManager().display_list_of_phrases_in_catalogue(entry[1])

                    for phrase in phrases:
                        add_phrase = KnowledgeManager().add_to_book(
                            current_client,
                            phrase,
                            current_user,
                            "vocabulary")

                    messages.success(request, (f"{catalogue_title} added!"))
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
                    pass

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

        entries = KnowledgeManager().display_open_book("vocabulary")
        if entries is None:
            messages.success(request, ("You've translated all the wordbook entries!"))
            return render(request, "translate_wordbook.html", {"entries": entries})
        else:
            if request.method == "POST":
                if request.POST["wordbook_action"] == "delete":
                    unique_id = request.POST["unique_id"]
                    delete_entry = KnowledgeManager().delete_book_entry(unique_id)

                    entries = KnowledgeManager().display_open_book("vocabulary")

                    if entries is None:
                        messages.success(request, ("You've translated all the wordbook entries!"))
                        return render(request, "translate_wordbook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "translate_wordbook.html", {"entries": entries})

                elif request.POST["wordbook_action"] == "save":
                    unique_id = request.POST["unique_id"]
                    polish = request.POST["polish"]

                    translate_entry = KnowledgeManager().translate_book_entry(unique_id, polish)
                    entries = KnowledgeManager().display_open_book("vocabulary")

                    if entries is None:
                        messages.success(request, ("You've translated all the wordbook entries!"))
                        return render(request, "translate_wordbook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "translate_wordbook.html", {"entries": entries})

            entries = entries[0]
            return render(request, "translate_wordbook.html", {"entries": entries})


@staff_member_required
def approve_wordbook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entries = KnowledgeManager().display_translated_book("vocabulary")
        if entries is None:
            messages.success(request, ("You've translated all the wordbook entries!"))
            return render(request, "approve_wordbook.html", {"entries": entries})
        else:
            if request.method == "POST":
                if request.POST["wordbook_action"] == "reject":
                    unique_id = request.POST["unique_id"]
                    delete_entry = KnowledgeManager().reject_book_entry(unique_id)

                    entries = KnowledgeManager().display_translated_book("vocabulary")

                    if entries is None:
                        messages.success(request, ("You've covered all the wordbook entries!"))
                        return render(request, "approve_wordbook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "approve_wordbook.html", {"entries": entries})

                elif request.POST["wordbook_action"] == "approve":
                    unique_id = request.POST["unique_id"]

                    approve_entry = KnowledgeManager().approve_book_entry(unique_id, current_user)
                    entries = KnowledgeManager().display_translated_book("vocabulary")

                    if entries is None:
                        messages.success(request, ("You've translated all the wordbook entries!"))
                        return render(request, "approve_wordbook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "approve_wordbook.html", {"entries": entries})

            entries = entries[0]
            return render(request, "approve_wordbook.html", {"entries": entries})


@staff_member_required
def translate_sentencebook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entries = KnowledgeManager().display_open_book("sentences")
        if entries is None:
            messages.success(request, ("You've translated all the sentencebook entries!"))
            return render(request, "translate_sentencebook.html", {"entries": entries})
        else:
            if request.method == "POST":
                if request.POST["sentencebook_action"] == "delete":
                    unique_id = request.POST["unique_id"]
                    delete_entry = KnowledgeManager().delete_book_entry(unique_id)

                    entries = KnowledgeManager().display_open_book("sentences")

                    if entries is None:
                        messages.success(request, ("You've translated all the sentencebook entries!"))
                        return render(request, "translate_sentencebook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "translate_sentencebook.html", {"entries": entries})

                elif request.POST["sentencebook_action"] == "save":
                    unique_id = request.POST["unique_id"]
                    polish = request.POST["polish"]

                    translate_entry = KnowledgeManager().translate_book_entry(unique_id, polish)
                    entries = KnowledgeManager().display_open_book("sentences")

                    if entries is None:
                        messages.success(request, ("You've translated all the sentencebook entries!"))
                        return render(request, "translate_sentencebook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "translate_sentencebook.html", {"entries": entries})

            entries = entries[0]
            return render(request, "translate_sentencebook.html", {"entries": entries})


@staff_member_required
def approve_sentencebook(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        entries = KnowledgeManager().display_translated_book("sentences")
        if entries is None:
            messages.success(request, ("You've translated all the sentencebook entries!"))
            return render(request, "approve_sentencebook.html", {"entries": entries})
        else:
            if request.method == "POST":
                if request.POST["sentencebook_action"] == "reject":
                    unique_id = request.POST["unique_id"]
                    delete_entry = KnowledgeManager().reject_book_entry(unique_id)

                    entries = KnowledgeManager().display_translated_book("sentences")

                    if entries is None:
                        messages.success(request, ("You've covered all the sentencebook entries!"))
                        return render(request, "approve_sentencebook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "approve_sentencebook.html", {"entries": entries})

                elif request.POST["sentencebook_action"] == "approve":
                    unique_id = request.POST["unique_id"]

                    approve_entry = KnowledgeManager().approve_book_entry(unique_id, current_user)
                    entries = KnowledgeManager().display_translated_book("sentences")

                    if entries is None:
                        messages.success(request, ("You've translated all the sentencebook entries!"))
                        return render(request, "approve_sentencebook.html", {"entries": entries})
                    else:
                        entries = entries[0]
                        return render(request, "approve_sentencebook.html", {"entries": entries})

            entries = entries[0]
            return render(request, "approve_sentencebook.html", {"entries": entries})


@staff_member_required
def upload_anki(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            client = request.POST["client"]
            deck = request.POST["deck"]
            txt_file = request.FILES["txt_file"]
            file = txt_file.read().decode("utf8")
            rows = file.splitlines()

            for row in rows:
                entry = row.split("\t")
                polish = entry[0]
                english = entry[1]

                VocabularyManager().add_entry(
                    client,
                    deck,
                    english,
                    polish,
                    current_user)

            messages.success(request, ("The file has been uploaded!"))
            return render(request, "upload_anki.html", {
                "clients": clients
                })

        return render(request, "upload_anki.html", {
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

                return redirect("prompts.html")

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
                    return redirect("prompts.html")

                else:
                    messages.error(request, ("The prompt already exists!"))
                    return redirect("prompts.html")

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

        memories = KnowledgeManager().display_memories(current_user)

        return render(request, "memories.html", {
            "memories": memories
            })


@staff_member_required
def upload_memories(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                KnowledgeManager().add_memory(
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4]
                    )

            messages.success(request, ("The file has been uploaded!"))
            return redirect("upload_memories")

        return render(request, "upload_memories.html", {})


@staff_member_required
def upload_pronunciation(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                KnowledgeManager().add_pronunciation(
                    entry[0],
                    entry[1],
                    entry[2]
                    )

            messages.success(request, ("The file has been uploaded!"))
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
                delete = StreamManager().delete_from_stream(unique_id)

                return redirect("stream.html")

            elif request.POST["stream_action"] == "explore":
                unique_id = request.POST["unique_id"]

                row = StreamManager().display_stream_entry(unique_id)

                return render(request, "stream_entry.html", {
                    "row": row
                    })

        return render(request, "stream.html", {})


@staff_member_required
def upload_stream(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                StreamManager().import_old_stream(
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4],
                    entry[5],
                    )

            messages.success(request, ("The file has been uploaded!"))
            return redirect("upload_stream.html")

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
def check_homework(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        uncompleted_assignments = CurriculumManager().display_uncompleted_assignments(current_client)
        completed_assignments = CurriculumManager().display_completed_assignments(current_client)

        if request.method == "POST":
            return render(request, "check_homework.html", {
                "uncompleted_assignments": uncompleted_assignments,
                "completed_assignments": completed_assignments
                })

        return render(request, "check_homework.html", {
                "uncompleted_assignments": uncompleted_assignments,
                "completed_assignments": completed_assignments
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
            return redirect("upload_sentence_stock.html")

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
def compose_set(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        sentences = SentenceManager().display_sentence_stock()
        next_set_id = SentenceManager().display_next_set_id()

        if request.method == "POST":
            if request.POST["action_on_set"] == "compose":
                set_id = request.POST["set_id"]
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
                    sentence_ids
                    )

                messages.success(request, ("Set created!"))
                return redirect("compose_set")

        return render(request, "compose_set.html", {
            "sentences": sentences,
            "next_set_id": next_set_id
            })


@staff_member_required
def display_sets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        items = SentenceManager().display_sets()

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

        if request.method == "POST":
            sentence_number = request.POST["sentence_number"]
            result = request.POST["result"]

            SentenceManager().grade_sentence(sentence_number, result, current_user)

            return redirect("grade_sentences.html")

        return render(request, "grade_sentences.html", {
            "entry": entry
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
            "positions": positions
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
            rating = request.POST["rating"]

            # Rating
            RatingManager().add_rating(client, link, rating)

            # Stream
            StreamManager().report_reading(client, link, current_user)

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

            StreamManager().report_reading(client, link, current_user)
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

            StreamManager().report_reading(client, link, current_user)
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

        if request.method == "POST":
            title = request.POST["title"]
            number_of_episodes = request.POST["number_of_episodes"]

            # Stream
            StreamManager().report_listening(
                client,
                title,
                number_of_episodes,
                current_user
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

                return redirect("repertoire.html")

            elif request.POST["repertoire_action"] == "delete":
                title = request.POST["title"]

                BackOfficeManager().delete_from_repertoire(
                    title
                    )

                return redirect("repertoire.html")

        return render(request, "repertoire.html", {
            "titles": titles
            })


@staff_member_required
def repertoire_line(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        title = BackOfficeManager().display_reported_repertoire_line()

        if title is None:
            messages.success(request, ("Everything's processed!"))
            return render(request, "repertoire_line.html", {})

        title_name = title[3]
        number_of_episodes = title[4]
        check_if_in = BackOfficeManager().check_if_in_repertoire(title_name)

        if request.method == "POST":
            if request.POST["repertoire_line_action"] == "add":
                stamp = request.POST["stamp"]
                date = request.POST["date"]
                client = request.POST["client"]
                title_name = request.POST["title"]
                number_of_episodes = request.POST["number_of_episodes"]
                duration = request.POST["duration"]
                title_type = request.POST["title_type"]
                status = request.POST["status"]

                if status == "not_in_stream":

                    if check_if_in is True:
                        # Repertoire line
                        BackOfficeManager().add_to_repertoire(
                            title_name,
                            duration,
                            title_type
                            )

                    # Stream
                    StreamManager().report_listening(
                        client,
                        title_name,
                        number_of_episodes,
                        current_user
                        )

                    BackOfficeManager().mark_repertoire_line_as_processed(stamp)

                    return redirect("repertoire_line")

                else:

                    # Stream
                    StreamManager().report_listening(
                        client,
                        title_name,
                        number_of_episodes,
                        current_user
                        )

                    BackOfficeManager().mark_repertoire_line_as_processed(stamp)

                    return redirect("repertoire_line")

            elif request.POST["repertoire_line_action"] == "remove":
                stamp = request.POST["stamp"]
                BackOfficeManager().remove_from_repertoire_line(stamp)

                return redirect("repertoire_line")

        return render(request, "repertoire_line.html", {
            "title": title
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

                assignments = SubmissionManager().download_graded_assignments(
                    start_date,
                    end_date
                    )

                file_paths = []

                for assignment in assignments:
                    date = assignment[0]
                    item = assignment[1]
                    name = assignment[2]
                    title = assignment[3]
                    wordcount = assignment[4]
                    flagged_content = assignment[5]
                    minor_errors = assignment[6]
                    major_errors = assignment[7]
                    reviewing_user = assignment[8]
                    comment = assignment[9]
                    grade = assignment[10]

                    path = DocumentManager().create_assignment_doc(
                        date,
                        item,
                        name,
                        title,
                        wordcount,
                        flagged_content,
                        minor_errors,
                        major_errors,
                        reviewing_user,
                        comment,
                        grade
                        )

                    file_path = os.path.join(django_settings.MEDIA_ROOT, path)
                    file_paths.append((path, file_path))

                zone = BytesIO()
                zip_file = ZipFile(zone, "w")

                for file_path in file_paths:
                    zip_file.write(file_path[1], file_path[0])

                zip_file.close()

                respone = HttpResponse(zone.getvalue(), content_type="application/x-zip-compressed")
                respone['Content-Disposition'] = 'attachment; filename=%s' % "assignments.zip"

                return respone

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
def display_roadmap_details(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        roadmap_details = RoadmapManager().roadmap_details(roadmap_id_number)
        course = roadmap_details[2]
        course_details = RoadmapManager().display_course(course)
        grades = RoadmapManager().display_grades(current_user, course)
        assessment_method = course_details[5]
        result = 0

        if assessment_method == "statistics":
            assessment_system = course_details[7]
            statistics = StreamManager().statistics(current_user)
            result = statistics[assessment_system]

        return render(request, "display_roadmap_details.html", {
            "roadmap_details": roadmap_details,
            "course_details": course_details,
            "assessment_method": assessment_method,
            "result": result
            })


@staff_member_required
def add_profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        client_names = ClientsManager().list_current_clients()

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
                    professors_title_status
                    )

                return render(request, "add_profile.html", {
                "client_names": client_names
                })

        return render(request, "add_profile.html", {
            "client_names": client_names
            })


@staff_member_required
def profiles(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profiles = RoadmapManager().display_profiles()

        if request.method == "POST":
            if request.POST["action_on_profile"] == "more":
                client_name = request.POST["client_name"]

                profile = RoadmapManager().display_profile(client_name)

                return render(request, "display_profile.html", {
                    "profile": profile
                    })

            if request.POST["action_on_profile"] == "edit":
                client_name = request.POST["client_name"]

                profile = RoadmapManager().display_profile(client_name)

                return render(request, "update_profile.html", {
                    "profile": profile
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
                    professors_title_status
                    )

                profiles = RoadmapManager().display_profiles()

                return render(request, "profiles.html", {
                    "profiles": profiles
                    })

        return render(request, "profiles.html", {
            "profiles": profiles
            })


@staff_member_required
def display_profile(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        profile = RoadmapManager().display_profile()

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

        user_agent = get_user_agent(request)
        rows = StreamManager().display_ranking()
        tags = BackOfficeManager().display_tags()

        if user_agent.is_mobile:
            return render(request, "m_ranking.html", {
                "rows": rows
                })

        return render(request, "ranking.html", {
            "rows": rows,
            "tags": tags
            })


@login_required
def statistics(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)
        stats = StreamManager().statistics(current_user)

        if user_agent.is_mobile:
            return render(request, "m_my_stats.html", {
                "stats": stats
                })
        else:
            return render(request, "statistics.html", {
                "stats": stats
                })


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

                return redirect(f"display_announcement/{notification_id}")

        return render(request, "announcements.html", {
            "announcements": announcements
            })


@login_required
def add_notification(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        clients = ClientsManager().list_current_users()

        if request.method == "POST":
            if request.POST["action_on_announcement"] == "publish":
                sender = current_user
                recipient = "all"
                subject = request.POST["subject"]
                content = request.POST["content"]
                notification_type = request.POST["notification_type"]
                status = "sent"

                BackOfficeManager().add_notification(
                    sender,
                    recipient,
                    subject,
                    content,
                    notification_type,
                    status
                    )

                return render(request, "add_notification.html", {
                    "clients": clients
                    })

        return render(request, "add_notification.html", {
            "clients": clients
            })


@login_required
def display_announcement(request, notification_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        announcement = BackOfficeManager().display_announcement(notification_id)
        stamp = TimeMachine().number_to_system_date_time(announcement[1])

        return render(request, "display_announcement.html", {
            "announcement": announcement,
            "stamp": stamp
            })


@staff_member_required
def add_grade(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        current_client = CurrentClientsManager().current_client(current_user)
        courses = RoadmapManager().display_current_courses(current_client)

        if request.method == "POST":
            student = current_client
            course = request.POST["course"]
            result = request.POST["result"]
            grade_type = request.POST["grade_type"]
            examiner = current_user

            RoadmapManager().add_grade(
                student,
                course,
                result,
                grade_type,
                examiner
                )

        return render(request, "add_grade.html", {
            "courses": courses
            })


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
def take_quiz(request, quiz_question_id, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        quiz = QuizManager().display_quiz(quiz_question_id)
        quiz_id = str(quiz_question_id)[:-2]

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
                    return redirect(f"/take_quiz/{next_quiz_question_id}/{item}")

            elif request.POST["answer"] == "leave":

                return redirect("assignments")

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


@login_required
def programs(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        programs = RoadmapManager().display_programs()

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
                return redirect("programs")

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

        return render(request, "courses.html", {
            "courses": courses
            })


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

        if request.method == "POST":
            if request.POST["action_on_timesheet"] == "filter":
                employee = request.POST["employee"]
                start = request.POST["start"]
                end = request.POST["end"]

                entries = AuditManager().display_entries(
                    employee,
                    start,
                    end
                    )

                return render(request, "timesheet.html", {
                    "entries": entries,
                    "current_user": current_user,
                    "employees": employees
                    })

        return render(request, "timesheet.html", {
            "current_user": current_user,
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

        clients = ClientsManager().list_current_users()
        ActivityManager().calculate_points_this_week("Joe Doe")

        if request.method == "POST":
            client = request.POST["client"]

            OnboardingManager().onboard_client(client, current_user)

            messages.success(request, ("Client onboarded!"))
            return redirect("onboard_client")

        return render(request, "onboard_client.html", {
            "clients": clients
            })

def footer(request):
    return render(request, "footer.html", {})