import os
import django
from django.db import connection
from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.sentence_manager import SentenceManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.vocabulary_manager import VocabularyManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class CurriculumPlanner:
    def __init__(self):
        today_pattern = "%Y-%m-%d"

    def plan_curriculum(
            self,
            item,
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
            ):

        component_type = assignment_type

        CurriculumManager().add_curriculum(
            item,
            deadline,
            client,
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
            set_details = SentenceManager().display_set(reference)
            set_id = set_details[0]
            sentence_ids = set_details[2]

            SentenceManager().compose_sentence_lists(
                client,
                item,
                set_id,
                sentence_ids,
                )

        elif assignment_type == "quiz":
            QuizManager().plan_quiz(client, item, reference)

    def plan_curricula(
            self,
            client,
            matrix,
            starting_date_number
            ):

        modules = CurriculumManager().display_matrix(matrix)

        i = 0
        for module in modules:
            component_id = module["component_id"]
            limit_number = module["limit_number"]

            entry = CurriculumManager().display_module(component_id)

            assignment_type = entry[1]
            title = entry[2]
            content = entry[3]
            resources = entry[4]
            conditions = entry[5]
            reference = entry[6]

            item = CurriculumManager().next_item() + i
            deadline_number = int(starting_date_number) + limit_number
            deadline = TimeMachine().number_to_system_date(deadline_number)

            self.plan_curriculum(
                item,
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

            i += 1