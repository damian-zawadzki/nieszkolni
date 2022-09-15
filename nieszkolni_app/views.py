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
import csv
import re
import json

from django_user_agents.utils import get_user_agent

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

        # If no button is clicked
        return render(request, 'view_answer.html', {"polish": polish, "english": english,  "old_due_today": old_due_today, "new_due_today": new_due_today, "problematic_due_today": problematic_due_today, "interval": interval})


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
    if request.method == "POST":
        internal_email_address = request.POST["internal_email_address"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password = request.POST["password"]
        username = first_name.lower() + last_name.lower()

        user = authenticate(request, username=username, password=password)
        if user is None:
            user = User.objects.create_user(username, internal_email_address, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, ("The student has been added to the database."))
            return redirect("home")

        else:
            messages.success(request, ("The student already exists."))

    return render(request, "register_user.html", {})


@staff_member_required
def register_client(request):
    coaches = ["Damian Zawadzki", "Marta Bańkowska", "Nadia Kukulska", "Piotr Gmitrzak"]
    levels = ["basic", "communicative", "advanced"]
    schools = ["Nieszkolni", "Secret Language Club"]

    if request.method == "POST":
        if request.POST["register"] == "client_and_user":

            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            name = first_name + " " + last_name
            school = request.POST["school"]
            password = request.POST["password"]
            phone_number = request.POST["phone_number"]
            contact_email_address = request.POST["contact_email_address"]
            internal_email_address = request.POST["internal_email_address"]
            meeting_duration = request.POST["meeting_duration"]
            price = request.POST["price"]
            acquisition_channel = request.POST["acquisition_channel"]
            recommenders = request.POST["recommenders"]
            coach = request.POST["coach"]
            level = request.POST["level"]
            test_user = request.POST["test_user"]
            username = first_name.lower() + last_name.lower()

            user = authenticate(request, username=username, password=password)
            if user is None:
                add = ClientsManager().add_client(
                    test_user,
                    name,
                    phone_number,
                    contact_email_address,
                    school,
                    internal_email_address,
                    meeting_duration,
                    price,
                    acquisition_channel,
                    recommenders,
                    coach,
                    level
                    )

                user = User.objects.create_user(username, internal_email_address, password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                messages.success(request, ("The student has been added to the database."))
                return render(request, "register_client.html", {
                    "coaches": coaches,
                    "levels": levels,
                    "schools": schools
                    })

            else:
                messages.error(request, ("The student could not be added to the database."))

            # else:
            #     messages.success(request, ("The student already exists."))
        elif request.POST["register"] == "client":
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            name = first_name + " " + last_name
            school = request.POST["school"]
            password = request.POST["password"]
            phone_number = request.POST["phone_number"]
            contact_email_address = request.POST["contact_email_address"]
            internal_email_address = request.POST["internal_email_address"]
            meeting_duration = request.POST["meeting_duration"]
            price = request.POST["price"]
            acquisition_channel = request.POST["acquisition_channel"]
            recommenders = request.POST["recommenders"]
            coach = request.POST["coach"]
            level = request.POST["level"]
            test_user = request.POST["test_user"]
            username = first_name.lower() + last_name.lower()

            is_client = ClientsManager().verify_client(name)
            if is_client is False:

                add = ClientsManager().add_client(
                    test_user,
                    name,
                    phone_number,
                    contact_email_address,
                    school,
                    internal_email_address,
                    meeting_duration,
                    price,
                    acquisition_channel,
                    recommenders,
                    coach,
                    level
                    )

                messages.success(request, ("The student has been added to the database."))
                return render(request, "register_client.html", {
                    "coaches": coaches,
                    "levels": levels,
                    "schools": schools
                    })        

            else:
                messages.error(request, ("The student is already in the database."))

        else:
            pass

    return render(request, "register_client.html", {
        "coaches": coaches,
        "levels": levels,
        "schools": schools
        })


@login_required
def options(request):
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

        if user_agent.is_mobile:
            return render(request, "m_profile.html", {})

        else:
            return render(request, "profile.html", {})


@login_required
def submit_assignment(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
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

        if request.method == "POST":
            item = request.POST["item"]

            return render(request, "assignments.html", {"item": item})

        else:
            uncomplated_assignments = CurriculumManager().display_uncompleted_assignments(current_user)
            complated_assignments = CurriculumManager().display_completed_assignments(current_user)

            return render(request, "assignments.html", {"uncomplated_assignments": uncomplated_assignments, "complated_assignments": complated_assignments})


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

        assignments = CurriculumManager().display_all_assignments()

        return render(request, "display_curricula.html", {"assignments": assignments})


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

                    print(entries)

                    if len(entries) == 0:
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

        rows = StreamManager().display_stream()

        if request.method == "POST":
            if request.POST["stream_action"] == "delete":
                unique_id = request.POST["unique_id"]
                delete = StreamManager().delete_from_stream(unique_id)

                return redirect("stream.html")

            if request.POST["stream_action"] == "explore":
                unique_id = request.POST["unique_id"]

                row = StreamManager().display_stream_entry(unique_id)

                return render(request, "stream_entry.html", {
                    "row": row
                    })

        return render(request, "stream.html", {
            "rows": rows
            })


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
                    "reported"
                    )

                return redirect("report_listening.html")

            else:
                duration = BackOfficeManager().get_duration_from_repertoire(title)
                final_duration = int(duration) * int(number_of_episodes)

                BackOfficeManager().add_to_repertoire_line(
                    current_user,
                    title,
                    number_of_episodes,
                    "processed"
                    )

                StreamManager().add_to_stream(
                    current_client,
                    "PO",
                    final_duration,
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
            title = request.POST["title"]
            number_of_episodes = request.POST["number_of_episodes"]
            duration = request.POST["duration"]
            title_type = request.POST["title_type"]
            final_duration = int(duration) * int(number_of_episodes)

            BackOfficeManager().add_to_repertoire(
                title,
                duration,
                title_type
                )

            StreamManager().add_to_stream(
                name,
                "PO",
                final_duration,
                current_user
                )

            BackOfficeManager().mark_repertoire_line_as_processed(stamp)

            return redirect("repertoire_line.html")

        if title is None:
            messages.success(request, ("Everything's processed!"))
            return render(request, "repertoire_line.html", {})

        title_name = title[3]
        check_if_in_repertoire = BackOfficeManager().check_if_in_repertoire(title_name)

        if check_if_in_repertoire is True:
            stamp = title[0]
            name = title[2]

            BackOfficeManager().mark_repertoire_line_as_processed(stamp)
            final_duration = BackOfficeManager().get_duration_from_repertoire(title_name)

            StreamManager().add_to_stream(
                name,
                "PO",
                final_duration,
                name
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

def footer(request):
    return render(request, "footer.html", {})