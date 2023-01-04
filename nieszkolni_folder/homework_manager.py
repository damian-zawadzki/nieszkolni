import os
import django
from django.db import connection
from django.contrib import messages

from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.knowledge_manager import KnowledgeManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class HomeworkManager:
    def __init__(self):
        pass

    def check_stats(self, item, current_user, command):
        if command == "flashcards_7":
            assignment = CurriculumManager().display_assignment(item)
            client = assignment[3]
            target = int(assignment[12])
            end = assignment[2]
            start = end - 7
            end_date = TimeMachine().number_to_system_date(end)
            start_date = TimeMachine().number_to_system_date(start)

            result = StreamManager().studied_days(client, start_date, end_date)

            if result >= target:

                CurriculumManager().change_status_to_completed(
                    item,
                    current_user
                    )

                output = ("SUCCESS", "Task completed!")

            else:
                difference = target - result
                output = ("WARNING", f"{difference} days still left! Keep up the good work!")

            return output

        elif command == "flashcards_sentences_7":
            assignment = CurriculumManager().display_assignment(item)
            client = assignment[3]
            target = int(assignment[12])
            end = assignment[2]
            start = end - 7
            end_date = TimeMachine().number_to_system_date(end)
            start_date = TimeMachine().number_to_system_date(start)

            result = StreamManager().studied_days_by_deck(
                client,
                start_date,
                end_date,
                "sentences"
                )

            if result >= target:

                CurriculumManager().change_status_to_completed(
                    item,
                    current_user
                    )

                product = ("SUCCESS", "Task completed!")

            else:
                difference = target - result
                product = ("WARNING", f"{difference} days still left! Keep up the good work!")

            return product

    def check_assignment(self, item, current_user):
        assignment_type_raw = CurriculumManager().display_assignment(item)
        assignment_type = assignment_type_raw[6]
        status = assignment_type_raw[11]

        if assignment_type == "reading" and status == "uncompleted":
            product = self.mark_as_read(item, current_user)
        else:
            product = self.mark_as_done(item, current_user)

        return product

    def mark_as_done(self, item, current_user):
        CurriculumManager().change_status_to_completed(
            item,
            current_user
            )

        product = ("SUCCESS", "Marked as done!")
        return product

    def mark_as_read(self, item, current_user):
        CurriculumManager().change_status_to_completed(
            item,
            current_user
            )

        position = CurriculumManager().check_position_in_library(item)
        value = position[2]

        assignment = CurriculumManager().display_assignment(item)
        client = assignment[3]

        StreamManager().add_to_stream(
            client,
            "PV",
            value,
            current_user
            )

        product = ("SUCCESS", "Marked as read!")
        return product

    def choose_action(self, item, current_user, action=None):
        assignment = CurriculumManager().display_assignment(item)

        if action is None:
            action = assignment[18]

        client = assignment[3]
        assignment_type = assignment[6]
        reference = assignment[16]
        command = assignment[19]
        output = None

        if action == "remove":

            CurriculumManager().remove_curriculum(item)

            product = ("check_homework", current_user)

        elif action == "submit":

            product = ("submit_assignment_automatically", item)

        elif action == "uncheck":

            CurriculumManager().change_status_to_fake_completed(
                    item,
                    current_user
                    )

            product = ("assignments", client)

        elif action == "mark_as_read":

            self.check_assignment(
                item,
                current_user
                )

            product = ("assignments", client)

        elif action == "mark_as_done":

            self.mark_as_done(
                item,
                current_user
                )

            product = ("assignments", client)

        elif action == "check_stats":

            output = HomeworkManager().check_stats(
                    item,
                    current_user,
                    command
                    )

            product = ("assignments", item, output)

        elif action == "take_quiz":

            product = ("take_quiz", item)

        elif action == "take_part":

            product = ("survey", item)

        elif action == "add_vocabulary":

            print(reference)

            output = KnowledgeManager().add_catalogue_to_book_by_no(
                client,
                reference,
                current_user,
                "vocabulary"
                )

            CurriculumManager().change_status_to_completed(
                    item,
                    current_user
                    )

            product = ("assignments", item, output)

        elif action == "translate":
            product = ("translate_sentences", item)

        elif action == "translate_text":

            list_number = SentenceManager().find_list_number_by_item(item)
            sentences = SentenceManager().display_sentence_list(list_number)
            product = ("translate_text", item)

        return product
