from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
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
import csv
import re
import json
import pyttsx3

from django_user_agents.utils import get_user_agent

from django.template import RequestContext

card_opening_time = 0


def home(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        total_phrases = VocabularyManager().total_cards(current_user)
        new_phrases = VocabularyManager().new_cards(current_user, "vocabulary")

        return render(request, 'home.html', {"total_phrases": total_phrases, "new_phrases": new_phrases})

    return render(request, 'home.html', {})

# def custom_error_view(request, *args, **argv):
#     return render(request, '500.html', status=500)


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
            interval = all_due_entries[0][4]
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
            interval = all_due_entries[0][4]
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
                interval = all_due_entries[0][4]

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
                try:
                    engine = pyttsx3.init()
                except:
                    pass

                try:
                    engine.stop()
                except:
                    pass

                deck = request.POST["deck"]

                all_due_entries = VocabularyManager().display_due_entries(current_user, deck)

                card_id = all_due_entries[0][0]
                polish = all_due_entries[0][1]
                english = all_due_entries[0][2]
                old_due_today = len(VocabularyManager().display_old_due_entries(current_user, deck))
                new_due_today = len(VocabularyManager().display_new_due_entries(current_user, deck))
                problematic_due_today = len(VocabularyManager().display_problematic_due_entries(current_user, deck))
                interval = all_due_entries[0][4]

                english_1 = re.sub(r"\ssb\s", " somebody ", english)
                english_2 = re.sub(r"\ssb$", " somebody", english_1)
                english_3 = re.sub(r"\ssth\s", " something ", english_2)
                english_4 = re.sub(r"\ssth$", " something", english_3)
                engine.say(english_4)

                try:
                    engine.runAndWait()
                    engine.stop()

                except:
                    pass

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
            return redirect("home")
        else:
            messages.error(request, ("Wrong password or username. Try again."))
            return redirect("login_user")

    else:
        return render(request, "login_user.html", {})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("Come back soon!"))
    return redirect("home")


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

                    add = ClientsManager().add_client(
                        username,
                        internal_email_address
                        )

                    user.save()

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
                internal_email_address = request.POST["internal_email_address"]
                meeting_duration = request.POST["meeting_duration"]
                price = request.POST["price"]
                acquisition_channel = request.POST["acquisition_channel"]
                recommenders = request.POST["recommenders"]
                reasons_for_resignation = request.POST["reasons_for_resignation"]
                status = request.POST["status"]
                coach = request.POST["coach"]
                level = request.POST["level"]
                daily_limit_of_new_cards = request.POST["daily_limit_of_new_cards"]


                edit = ClientsManager().edit_client(
                    user_type,
                    name,
                    phone_number,
                    contact_email_address,
                    internal_email_address,
                    meeting_duration,
                    price,
                    acquisition_channel,
                    recommenders,
                    reasons_for_resignation,
                    status,
                    coach,
                    level,
                    daily_limit_of_new_cards
                    )

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
                daily_limit_of_new_cards = client_details[14]

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
                    "daily_limit_of_new_cards": daily_limit_of_new_cards
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

        if request.method == "POST":
            current_daily_limit_of_new_cards = request.POST["new_daily_limit_of_new_cards"]
            print(current_daily_limit_of_new_cards)
            change_the_limit = VocabularyManager().update_current_daily_limit_of_new_cards(current_user, current_daily_limit_of_new_cards)

            return render(request, "options.html", {"current_daily_limit_of_new_cards": current_daily_limit_of_new_cards})

        current_daily_limit_of_new_cards = VocabularyManager().current_daily_limit_of_new_cards(current_user)

        return render(request, "options.html", {"current_daily_limit_of_new_cards": current_daily_limit_of_new_cards})


@staff_member_required
def staff(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        return render(request, "staff.html", {})


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
                roadmap_id_number = request.POST["roadmap_id_number"]
                roadmap_details = RoadmapManager().display_roadmap_details(roadmap_id_number)
                course = roadmap_details[2]
                course_details = RoadmapManager().display_course(course)
                grades = RoadmapManager().display_grades(current_user, course)
                result = RoadmapManager().display_final_grade(current_user, course)
                threshold = RoadmapManager().display_course_threshold(course)

                if result >= threshold:
                    status = "passed"
                elif result == -1:
                    status = "ongoing"
                else:
                    status = "failed"

                RoadmapManager().update_roadmap(roadmap_id_number, status)

                deadline = TimeMachine().number_to_system_date(roadmap_details[4])

                return render(request, "display_roadmap_details.html", {
                    "roadmap_details": roadmap_details,
                    "course_details": course_details,
                    "deadline": deadline,
                    "grades": grades,
                    "status": status
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
                "target": target
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
                "target": target
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
                name = request.POST["client"]

                CurriculumManager().remove_curriculum(item)

                return redirect("display_curricula.html")

            if request.POST["go_to"] == "submission":
                item = request.POST["item"]
                current_user = request.POST["current_user"]
                assignment_type = request.POST["assignment_type"]

                return render(request, "submit_assignment_automatically.html", {
                    "item": item,
                    "name": current_user,
                    "assignment_type": assignment_type
                    })

            if request.POST["go_to"] == "marking_as_read":
                item = request.POST["item"]
                current_user = request.POST["current_user"]

                check = CurriculumManager().change_status_to_completed(
                    item,
                    current_user
                    )

                position = CurriculumManager().check_position_in_library(item)
                value = position[2]

                StreamManager().add_to_stream(
                    current_user,
                    "PV",
                    value,
                    current_user
                    )

                return redirect("assignments.html")

            elif request.POST["go_to"] == "translation":
                item = request.POST["item"]
                current_user = request.POST["current_user"]
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                list_number = request.POST["title"]
                list_number = list_number.replace("Translate ", "")
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
                name = request.POST["name"]
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

        if request.method == "POST":
            unique_id = request.POST["unique_id"]

            submission = SubmissionManager().display_students_assignment(unique_id)
            assignment_type = submission[10]

            if assignment_type != "sentences":

                return render(request, "submission_entry.html", {
                        "submission": submission
                        })

            else:
                date = submission[0]
                title = submission[1]
                status = submission[9]
                sentence_number = title.replace("Translate ", "")
                sentences = SentenceManager().display_graded_list(sentence_number)

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
            return redirect("upload_curriculum.html")

        return render(request, "upload_curriculum.html", {})


@staff_member_required
def add_curriculum(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        names = ClientsManager().list_current_clients()

        if request.method == "POST":
            if request.POST["curriculum_action"] == "choose_filters":
                name = request.POST["name"]
                names = [name]
                assignment_type = request.POST["assignment_type"]

                if assignment_type == "sentences":
                    entries = SentenceManager().display_planned_sentence_lists_per_student(name)
                elif assignment_type == "reading":
                    entries = BackOfficeManager().display_library_position_numbers()
                else:
                    entries = ""

                return render(request, "add_curriculum_2.html", {
                    "names": names,
                    "assignment_type": assignment_type,
                    "entries": entries
                    })

            else:
                item = CurriculumManager().next_item()
                deadline = request.POST["deadline"]
                name = request.POST["name"]
                component_id = "custom_task_9999"
                component_type = "custom_task"
                assignment_type = request.POST["assignment_type"]
                title = request.POST["title"]
                content = request.POST["content"]
                matrix = "custom matrix"
                reference = request.POST["reference"]

                if assignment_type == "reading":
                    position = BackOfficeManager().find_position_in_library(reference)
                    resources = position[3]
                else:
                    resources = request.POST["resources"]

                conditions = request.POST["conditions"]

                CurriculumManager().add_curriculum(
                    item,
                    deadline,
                    name,
                    component_id,
                    component_type,
                    assignment_type,
                    title,
                    content,
                    matrix,
                    resources,
                    conditions,
                    reference
                    )

                if assignment_type == "sentences":
                    list_number = title.replace("Translate ", "")
                    SentenceManager().mark_sentence_list_as_planned(list_number)

                messages.success(request, ("Curriculum extended!"))
                return render(request, "add_curriculum.html", {
                    "names": names
                    })

        return render(request, "add_curriculum.html", {
            "names": names
            })


@login_required
def assignments(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        user_agent = get_user_agent(request)

        if request.method == "POST":
            item = request.POST["item"]

            return render(request, "assignments.html", {"item": item})

        else:

            uncomplated_assignments = CurriculumManager().display_uncompleted_assignments(current_user)
            complated_assignments = CurriculumManager().display_completed_assignments(current_user)

            if user_agent.is_mobile:
                return render(request, "m_my_to_do_list.html", {
                    "uncomplated_assignments": uncomplated_assignments,
                    "complated_assignments": complated_assignments
                    })

            else:
                return render(request, "assignments.html", {
                    "uncomplated_assignments": uncomplated_assignments,
                    "complated_assignments": complated_assignments
                    })


@login_required
def assignment(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            item = request.POST["item"]

            if request.POST["go_to"] == "assignment":

                assignment = CurriculumManager().display_assignment(item)

                if request.POST["go_to"] != "submission":
                    return render(request, "assignment.html", {
                        "assignment": assignment,
                        "current_user": current_user
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
        print(entries)

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
                print(module)

                return render(request, "display_module.html", {
                    "module": module
                    })

        return render(request, "display_modules.html", {
            "modules": modules
            })


@staff_member_required
def add_module(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            component_id_number = request.POST["component_id_number"]
            component_type = request.POST["component_type"]
            component_id = f"{component_type}_{component_id_number}"
            title = request.POST["title"]
            content = request.POST["content"]
            resources = request.POST["resources"]
            conditions = request.POST["conditions"]

            CurriculumManager().add_module(
                component_id,
                component_type,
                title,
                content,
                resources,
                conditions
                )

            messages.success(request, ("You have added a module!"))
            return render(request, "add_module.html", {})

        return render(request, "add_module.html", {})


@staff_member_required
def display_matrices(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = CurriculumManager().display_matrices()

        if request.method == "POST":
            matrix = request.POST["matrix"]
            modules = CurriculumManager().display_matrix(matrix)

            return render(request, "display_matrices.html", {
                "modules": modules,
                "matrices": matrices
                })

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

        if request.method == "POST":
            component_id = request.POST["component_id"]
            matrix = request.POST["matrix"]
            limit_number = request.POST["limit_number"]

            CurriculumManager().add_matrix(
                component_id,
                matrix,
                limit_number
                )

            messages.success(request, ("You have updated the matrix!"))
            return render(request, "add_matrix.html", {
                "components": components
                })

        return render(request, "add_matrix.html", {
            "components": components
            })


@staff_member_required
def plan_matrix(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        matrices = CurriculumManager().display_matrices()
        clients = ClientsManager().list_current_clients()

        if request.method == "POST":
            client = request.POST["client"]
            matrix = request.POST["matrix"]
            starting_date = request.POST["starting_date"]
            starting_date_number = TimeMachine().date_to_number(starting_date)

            modules = CurriculumManager().display_matrix(matrix)

            i = 0
            for module in modules:
                component_id = module["component_id"]
                limit_number = module["limit_number"]

                entry = CurriculumManager().display_module(component_id)

                component_type = entry[1]
                title = entry[2]
                content = entry[3]
                resources = entry[4]
                conditions = entry[5]

                item = CurriculumManager().next_item() + i
                deadline = starting_date_number + limit_number
                deadline_date = TimeMachine().number_to_system_date(deadline)
                component_type_raw = re.search(r"\w.+_", component_id).group()
                component_type = re.sub("_", "", component_type_raw)
                reference = 0

                CurriculumManager().add_curriculum(
                    item,
                    deadline_date,
                    client,
                    component_id,
                    component_type,
                    component_type,
                    title,
                    content,
                    matrix,
                    resources,
                    conditions,
                    reference
                    )

                i += 1

                x = (
                    item,
                    deadline_date,
                    client,
                    component_id,
                    component_type,
                    component_type,
                    title,
                    content,
                    matrix,
                    resources,
                    conditions,
                    reference
                    )

                print(x)

            messages.success(request, ("You have planned a curriculum!"))
            return render(request, "plan_matrix.html", {
                "matrices": matrices,
                "clients": clients
                })

        return render(request, "plan_matrix.html", {
            "matrices": matrices,
            "clients": clients
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
            return redirect("switch_clients.html")

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

                add_to_wordbook = KnowledgeManager().add_to_book(current_client, entry, current_user, "vocabulary")

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

            elif request.POST["add_knowledge"] == "add_sentencebook":
                entry = request.POST["sentencebook_entry"]
                print(entry)

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

                add_memory = KnowledgeManager().add_memory(current_user, current_client, prompt, left_option, right_option)

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
def upload_sets(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            file = csv_file.read().decode("utf8")
            entries = StringToCsv().convert(file)

            for entry in entries:
                upload_sentence_stock = SentenceManager().upload_sets(
                    entry[0],
                    entry[1]
                    )

            messages.success(request, ("The file has been uploaded!"))
            return redirect("upload_sets.html")

        return render(request, "upload_sets.html", {})


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
                entries = SentenceManager().display_planned_sentences_per_student(name)

                return render(request, "composed_sentences.html", {
                    "current_clients": current_clients,
                    "entries": entries,
                    })
            else:
                name = request.POST["name"]
                entries = SentenceManager().display_planned_sentence_lists_per_student(name)

                return render(request, "composed_sentences.html", {
                    "current_clients": current_clients,
                    "entries": entries
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

                return redirect("library.html")

            else:
                position_number = request.POST["position_number"]

                BackOfficeManager().delete_from_library(
                    position_number,
                    )

                return redirect("library.html")

        return render(request, "library.html", {
            "positions": positions
            })


@login_required
def report_reading(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            link = request.POST["link"]

            check_if_in_library = BackOfficeManager().check_if_in_library(link)

            if check_if_in_library is False:

                BackOfficeManager().add_to_library_line(
                    current_user,
                    link,
                    "reported"
                    )

                return redirect("report_reading.html")

            else:
                wordcount = BackOfficeManager().get_wordcount_from_library(link)

                BackOfficeManager().add_to_library_line(
                    current_user,
                    link,
                    "processed_automatically"
                    )

                StreamManager().add_to_stream(
                    current_user,
                    "PV",
                    wordcount,
                    current_user
                    )

                return redirect("report_reading.html")

        return render(request, "report_reading.html", {})


@staff_member_required
def library_line(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        link = BackOfficeManager().display_reported_library_line()

        if request.method == "POST":
            position_number = BackOfficeManager().next_custom_postion_number()
            title = request.POST["title"]
            wordcount = request.POST["wordcount"]
            link = request.POST["link"]
            name = request.POST["name"]

            BackOfficeManager().add_to_library(
                position_number,
                title,
                wordcount,
                link
                )

            StreamManager().add_to_stream(
                name,
                "PV",
                wordcount,
                current_user
                )

            BackOfficeManager().mark_library_line_as_processed(name, link)

            return redirect("library_line.html")

        if link is None:
            messages.success(request, ("Everything's processed!"))

            return render(request, "library_line.html", {})

        url = link[1]
        check_if_in_library = BackOfficeManager().check_if_in_library(url)

        if check_if_in_library is True:
            name = link[0]

            wordcount = BackOfficeManager().get_wordcount_from_library(url)

            BackOfficeManager().mark_library_line_as_processed(name, url)

            StreamManager().add_to_stream(
                name,
                "PV",
                wordcount,
                name
                )

            return redirect("library_line.html")

        return render(request, "library_line.html", {
            "link": link
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

        current_client = CurrentClientsManager().current_client(current_user)
        titles = BackOfficeManager().display_titles()

        if request.method == "POST":
            title = request.POST["title"]
            number_of_episodes = request.POST["number_of_episodes"]

            check_if_in_repertoire = BackOfficeManager().check_if_in_repertoire(title)

            if check_if_in_repertoire is False:

                BackOfficeManager().add_to_repertoire_line(
                    current_client,
                    title,
                    number_of_episodes,
                    "not_in_stream"
                    )

                return redirect("report_listening.html")

            else:
                StreamManager().add_to_stream(
                    current_client,
                    "PO",
                    f'{title} *{number_of_episodes}',
                    current_user
                    )

                return redirect("report_listening.html")

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

            else:
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

        if request.method == "POST":
            stamp = request.POST["stamp"]
            date = request.POST["date"]
            name = request.POST["name"]
            title_name = request.POST["title"]
            number_of_episodes = request.POST["number_of_episodes"]
            duration = request.POST["duration"]
            title_type = request.POST["title_type"]
            status = request.POST["status"]

            if status == "not_in_stream":

                BackOfficeManager().add_to_repertoire(
                    title_name,
                    duration,
                    title_type
                    )

                StreamManager().add_to_stream(
                    name,
                    "PO",
                    f'{title_name} *{number_of_episodes}',
                    current_user
                    )

                BackOfficeManager().mark_repertoire_line_as_processed(stamp)

                return redirect("repertoire_line.html")

            else:

                BackOfficeManager().add_to_repertoire(
                    title_name,
                    duration,
                    title_type
                    )

                BackOfficeManager().mark_repertoire_line_as_processed(stamp)

                return redirect("repertoire_line.html")
        if title is None:
            messages.success(request, ("Everything's processed!"))
            return render(request, "repertoire_line.html", {})

        title_name = title[3]
        number_of_episodes = title[4]
        check_if_in_repertoire = BackOfficeManager().check_if_in_repertoire(title_name)

        if check_if_in_repertoire is True:
            stamp = title[0]
            name = title[2]

            BackOfficeManager().mark_repertoire_line_as_processed(stamp)

            StreamManager().add_to_stream(
                name,
                "PO",
                f'{title_name} *{number_of_episodes}',
                current_user
                )

            return redirect("repertoire_line.html")

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
            start_date = request.POST["start_date"]
            end_date = request.POST["end_date"]

            assignments = SubmissionManager().download_graded_assignments(
                start_date,
                end_date
                )

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

                file = DocumentManager().create_assignment_doc(
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

                print(file)

            return redirect("download_assignments.html")

        return render(request, "download_assignments.html", {})

@staff_member_required
def add_course(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

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

                RoadmapManager().add_course(
                    course,
                    course_type,
                    course_description,
                    registration_description,
                    assessment_description,
                    assessment_method,
                    link,
                    reference_system,
                    threshold
                    )

                courses = RoadmapManager().list_courses()
                return render(request, "list_courses.html", {"courses": courses})

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

                RoadmapManager().update_course(
                    course,
                    course_type,
                    course_description,
                    registration_description,
                    assessment_description,
                    assessment_method,
                    link,
                    reference_system,
                    threshold
                    )

                courses = RoadmapManager().list_courses()
                return render(request, "list_courses.html", {"courses": courses})      

        return render(request, "add_course.html", {})


@staff_member_required
def list_courses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_course"] == "more":
                course = request.POST["course"]
                course = RoadmapManager().display_course(course)

                return render(request, "display_course.html", {"course": course})

            if request.POST["action_on_course"] == "edit":
                course = request.POST["course"]
                course = RoadmapManager().display_course(course)
                print(course)

                return render(request, "update_course.html", {"course": course})

        courses = RoadmapManager().list_courses()

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
                deadline = name = request.POST["deadline"]

                RoadmapManager().add_roadmap(
                    client,
                    semester,
                    course,
                    deadline,
                    current_user
                    )

                return render(request, "add_roadmap.html", {
                    "names": names,
                    "courses": courses
                    })

        return render(request, "add_roadmap.html", {
            "names": names,
            "courses": courses
            })


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

        return render(request, "display_roadmap_details.html", {
            "roadmap_details": roadmap_details,
            "course_details": course_details
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

            if request.POST["action_on_roadmaps"] == "more":
                roadmap_id_number = request.POST["roadmap_id_number"]
                roadmap_details = RoadmapManager().display_roadmap_details(roadmap_id_number)
                course = roadmap_details[2]
                course_details = RoadmapManager().display_course(course)
                grades = RoadmapManager().display_grades(current_user, course)

                deadline = TimeMachine().number_to_system_date(roadmap_details[4])

                return render(request, "display_roadmap_details.html", {
                    "roadmap_details": roadmap_details,
                    "course_details": course_details,
                    "deadline": deadline,
                    "grades": grades
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

        if user_agent.is_mobile:
            return render(request, "m_ranking.html", {
                "rows": rows
                })

        return render(request, "ranking.html", {
            "rows": rows
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

        announcements = BackOfficeManager().display_announcements()\

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

        notification_id = notification_id

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


def footer(request):
    return render(request, "footer.html", {})