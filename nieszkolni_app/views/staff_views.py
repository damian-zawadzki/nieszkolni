from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.db import transaction
from django.db import IntegrityError

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


@staff_member_required
def product_process(request):

    context = {}

    return render(
        request,
        "product_process.html",
        context
        )


@staff_member_required
def add_product(request):

    categories = KnowledgeManager().display_prompts("product_category")
    courses = RoadmapManager().list_courses()

    if request.method == "POST":
        if request.POST["action_on_product"] == "add":
            ProductManager().add_product(
                title=request.POST["title"],
                description=request.POST["description"],
                category=request.POST["category"],
                points=request.POST["points"],
                quantity=request.POST["quantity"],
                allocation_per_client=request.POST["allocation_per_client"],
                status=request.POST["status"],
                image=request.POST["image"],
                reference=request.POST["reference"]
                )

            messages.success(request, ("Product added"))
            return redirect("product_process")

        elif request.POST["action_on_product"] == "filter":
            category = request.POST["category"]

            if category == "course":
                data = json.dumps(list(Course.objects.all().values()))

            elif category == "vocabulary":
                data = json.dumps(list(Catalogue.objects.all().values(
                    "catalogue_number",
                    "catalogue_name"
                    ).distinct()
                    ))

            return HttpResponse(data)

    context = {
        "categories": categories,
        "courses": courses
        }

    return render(
        request,
        "add_product.html",
        context
        )


@login_required
def products(request):

    products = Product.objects.filter(status="available").order_by("-creation_stamp")
    context = {
        "products": products
        }

    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(
            request,
            "m_products.html",
            context
            )
    else:
        return render(
            request,
            "products.html",
            context
            )


@login_required
def product(request, product_id):

    product = Product.objects.get(pk=product_id)
    context = {
        "product_id": product_id,
        "product": product
        }

    if request.method == "POST":
        if request.POST["action_on_product"] == "update":
            return redirect("update_product", product_id=product_id)

        elif request.POST["action_on_product"] == "sign_up":

            outputs = ProductManager().run_order(
                    product_id,
                    get_current_user(request)
                    )
            for output in outputs:
                messages.add_message(
                    request,
                    getattr(messages, output[0]),
                    output[1]
                    )
            return redirect("products")

    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(
            request,
            "m_product.html",
            context
            )
    else:
        return render(
            request,
            "product.html",
            context
            )


@staff_member_required
def update_product(request, product_id):

    product = Product.objects.get(pk=product_id)
    courses = RoadmapManager().list_courses()

    context = {
        "product_id": product_id,
        "product": product,
        "courses": courses
        }

    if request.method == "POST":
        if request.POST["action_on_product"] == "update":
            ProductManager().update_product(
                title=request.POST["title"],
                description=request.POST["description"],
                category=request.POST["category"],
                points=request.POST["points"],
                quantity=request.POST["quantity"],
                allocation_per_client=request.POST["allocation_per_client"],
                status=request.POST["status"],
                image=request.POST["image"],
                reference=request.POST["reference"],
                product_id=product_id
                )

            messages.success(request, ("Product updated"))
            return redirect("products")

    return render(
        request,
        "update_product.html",
        context
        )

# Surveys


@staff_member_required
def survey_process(request):

    context = {}

    return render(
        request,
        "survey_process.html",
        context
        )


@staff_member_required
def add_survey_option(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        options = SurveyManager().display_options()

        if request.method == "POST":
            if request.POST["action_on_survey"] == "add":
                option = request.POST["option"]
                option_value = request.POST["option_value"]

                SurveyManager().add_option(option, option_value)

                messages.success(request, "Option added")
                return redirect("add_survey_option")

        return render(request, "add_survey_option.html", {
            "options": options
            })


@staff_member_required
def add_survey_question(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        options = SurveyManager().display_options()
        questions = SurveyManager().display_questions()

        if request.method == "POST":
            if request.POST["action_on_survey"] == "add":
                question = request.POST["question"]
                question_type = request.POST["question_type"]
                options = request.POST.getlist("option")
                action = request.POST["action"]
                description = request.POST["description"]

                option_ids = ";".join(options)

                SurveyManager().add_question(
                        question,
                        question_type,
                        option_ids,
                        action,
                        description
                        )

                messages.success(request, "Question added")
                return redirect("add_survey_question")

        return render(request, "add_survey_question.html", {
            "options": options,
            "questions": questions
            })


@staff_member_required
def display_survey_question(request, question_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        question = SurveyManager().display_question(question_id)[0]
        options = SurveyManager().display_question(question_id)[1]

        return render(request, "display_survey_question.html", {
            "question_id": question_id,
            "question": question,
            "options": options
            })


@staff_member_required
def add_survey(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_survey"] == "add":
                title = request.POST["title"]
                content = request.POST["content"]

                SurveyManager().add_survey(
                    title,
                    content
                    )

                messages.success(request, "Survey created")
                return redirect("display_surveys")

        return render(request, "add_survey.html", {})


@staff_member_required
def display_surveys(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        surveys = SurveyManager().display_surveys()

        return render(request, "display_surveys.html", {
            "surveys": surveys
            })


@staff_member_required
def display_survey(request, survey_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        survey = SurveyManager().display_survey(survey_id)
        questions = SurveyManager().display_questions_by_survey(survey_id)

        return render(request, "display_survey.html", {
            "survey_id": survey_id,
            "survey": survey,
            "questions": questions
            })


@staff_member_required
def add_question_to_survey(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        surveys = SurveyManager().display_surveys()
        questions = SurveyManager().display_questions()

        if request.method == "POST":
            if request.POST["action_on_survey"] == "add":
                survey_id = request.POST["survey_id"]
                question_id = request.POST["question_id"]

                SurveyManager().add_question_to_survey(
                    survey_id,
                    question_id
                    )

                messages.success(request, "Question added to the survey")
                return redirect("add_question_to_survey")

        return render(request, "add_question_to_survey.html", {
            "surveys": surveys,
            "questions": questions
            })


@login_required
def survey(request, item):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        data = SurveyManager().take_survey(item)

        if data is None:
            CurriculumManager().change_status_to_completed(item, current_user)
            page = SubmissionManager().find_landing_page(item)

            if page[0] == "applause":
                return redirect("applause", activity_points=page[1])
            else:
                return redirect("completed")

        response_id = data[0]
        question = data[1]
        options = data[2]
        count = data[3]
        total = data[4]

        if request.method == "POST":
            response = request.POST["response"]

            if question.action != "none":
                SurveyManager().perform_action(
                    item,
                    question.action,
                    response,
                    current_user
                    )

            SurveyManager().respond(response, response_id)

            return redirect("survey", item=item)

        return render(request, "survey.html", {
            "item": item,
            "question": question,
            "options": options,
            "count": count,
            "total": total
            })


@login_required
def completed(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.method == "POST":
            if request.POST["action_on_completed"] == "leave":
                return redirect("campus")

        return render(request, "completed.html", {})


@staff_member_required
def responses(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        questions = SurveyManager().display_questions()

        if request.method == "POST":
            if request.POST["action_on_responses"] == "filter":
                question_id = request.POST["question_id"]

                responses = SurveyManager().display_responses(question_id)

                return render(request, "responses.html", {
                    "questions": questions,
                    "responses": responses
                    })

        return render(request, "responses.html", {
            "questions": questions,
            })

# Cards


@staff_member_required
def card_process(request):

    context = {}

    return render(
        request,
        "card_process.html",
        context
        )


@staff_member_required
def display_cards(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        cards = VocabularyManager().display_all_cards()

        if request.method == "POST":
            if request.POST["action_on_cards"] == "open":
                card_id_raw = request.POST["card_id"]
                card_id = card_id_raw.split(": ")[0]

                return redirect("display_card", card_id=card_id)

        context = {
            "cards": cards,
            }

        return render(request, "display_cards.html", context)


@staff_member_required
def display_card(request, card_id):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        card = VocabularyManager().display_card(
                card_id
                )

        if request.method == "POST":
            if request.POST["action_on_card"] == "remove":

                VocabularyManager().remove_cards(card_id)

                return redirect("display_cards")

            elif request.POST["action_on_card"] == "edit":
                english = request.POST["english"]
                polish = request.POST["polish"]

                VocabularyManager().edit_cards(
                    card_id,
                    english,
                    polish
                    )

                return redirect("display_card", card_id=card_id)

            elif request.POST["action_on_card"] == "back":
                return redirect("display_cards")

        context = {
            "card_id": card_id,
            "card": card
            }

        return render(request, "display_card.html", context)