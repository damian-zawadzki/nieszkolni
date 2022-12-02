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

                product = ("SUCCESS", "Task completed!")

            else:
                difference = target - result
                product = ("WARNING", f"{difference} days still left! Keep up the good work!")

            return product

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