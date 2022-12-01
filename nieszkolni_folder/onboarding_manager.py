import os
import django
from django.db import connection
from nieszkolni_app.models import Pronunciation
from nieszkolni_app.models import Dictionary
from nieszkolni_app.models import Prompt
from nieszkolni_app.models import Question
from nieszkolni_app.models import Quiz
from nieszkolni_app.models import Assessment
from nieszkolni_app.models import Collection
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.vocabulary_manager import VocabularyManager
from nieszkolni_folder.cleaner import Cleaner

import random
import re

from nieszkolni_folder.sentence_manager import SentenceManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.vocabulary_manager import VocabularyManager

from nieszkolni_folder.knowledge_manager import KnowledgeManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class OnboardingManager:
    def __init__(self):
        pass

    def onboard_client(self, client, current_user):
        self.add_wordbook(client, current_user)
        self.add_pronunciation(client, current_user)
        self.add_memories(client, current_user)

    def add_wordbook(self, client, current_user):
        entries = [
            "to go abroad",
            "to go dancing",
            "to go downtown",
            "to go east",
            "to go for a beer",
            "to go for a coffee",
            "to go for a drink",
            "to go for a ride",
            "to go for a run; to go running",
            "to go for a walk",
            "to go home",
            "to go north",
            "to go on a date",
            "to go on a diet",
            "to go on a trip",
            "to go on an adventure",
            "to go on sick leave",
            "to go on stage",
            "to go on strike",
            "to go on vacation",
            "to go shopping",
            "to go south",
            "to go to a bar",
            "to go to a concert",
            "to go to a conference",
            "to go to a festival",
            "to go to a meeting",
            "to go to a party",
            "to go to a restaurant",
            "to go to bed",
            "to go to church",
            "to go to dinner",
            "to go to jail; to go to prison",
            "to go to school",
            "to go to sleep",
            "to go to the airport",
            "to go to the army",
            "to go to the bank",
            "to go to the bathroom",
            "to go to the beach",
            "to go to the bedroom",
            "to go to the doctor",
            "to go to the gym",
            "to go to the hospital",
            "to go to the kitchen",
            "to go to the lake",
            "to go to the living room",
            "to go to the movies",
            "to go to the park",
            "to go to the store",
            "to go to the swimming pool",
            "to go to university",
            "to go to work",
            "to go west"
            ]

        for entry in entries:
            KnowledgeManager().add_to_book(
                client,
                entry,
                current_user,
                "vocabulary"
                )

    def add_pronunciation(self, client, current_user):
        entries = [
            "their",
            "to focus",
            "won",
            "saw",
            "a course",
            "ZUI",
            "GL",
            "HF",
            "LMAO",
            "IG"
            ]

        for entry in entries:
            KnowledgeManager().add_pronunciation(
                client,
                entry,
                current_user
                )

    def add_memories(self, client, current_user):
        entries = [
            ("past", "catch", ""),
            ("comma before", "if", ""),
            ("difference", "realise", "realize")
            ]

        for entry in entries:
            print(entry)
            KnowledgeManager().add_memory(
                current_user,
                client,
                entry[0],
                entry[1],
                entry[2]
                )