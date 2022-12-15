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
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.back_office_manager import BackOfficeManager
from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.clients_manager import ClientsManager
from nieszkolni_folder.knowledge_manager import KnowledgeManager


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class ActivityManager:
    def __init__(self):
        pass

    def calculate_points_this_week(self, client):
        today = TimeMachine().today_number()
        last_sunday = TimeMachine().last_sunday()
        this_sunday = TimeMachine().this_sunday()

        assignments = CurriculumManager().assignments_and_status_from_to(
                client,
                last_sunday,
                this_sunday
                )

        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")
        po = StreamManager().count_po_from_to(client, last_sunday, this_sunday)
        stats = StreamManager().statistics(client)
        duration = stats["duration"]
        flashcards_check = stats["study_days_this_week"]

        no_homework = BackOfficeManager().display_option_by_command("no_homework_ap")
        full_homework = BackOfficeManager().display_option_by_command("full_homework_ap")
        main_homework = BackOfficeManager().display_option_by_command("main_homework_ap")

        no_homework = no_homework[0]
        full_homework = full_homework[0]
        main_homework = main_homework[0]

        check = {
            "minimum": False,
            "maximum": False,
            "attendance": False
            }

        completed = []
        uncompleted = []

        for assignment in assignments:
            if assignment[2] not in no_submissions:
                deadline = assignment[1]
                completion_date = assignment[4]

                if completion_date > deadline:
                    uncompleted.append(assignment[0])

                elif completion_date == 0 and deadline < today:
                    uncompleted.append(assignment[0])

                else:
                    completed.append(assignment[0])

        if len(uncompleted) == 0:
            check.update({"maximum": True})

        if po > 30 and flashcards_check > 2:
            check.update({"minimum": True})

        if duration > 0:
            check.update({"attendance": True})

        minimum = check["minimum"]
        maximum = check["maximum"]
        attendance = check["attendance"]

        score = 0

        if minimum is False:
            score = no_homework
        else:
            if maximum is True:
                score = full_homework
            else:
                score = main_homework

        if attendance is True and minimum is not False:
            score *= 2

        return score

    def check_if_settle_this_week(self):
        week_sign = TimeMachine().this_week_number_sign()
        rows = StreamManager().find_by_command("Settle activity")

        weeks = [row[5] for row in rows]

        if week_sign in weeks:
            return True
        else:
            return False

    def settle_last_week_activity(self, current_user):
        week_sign = TimeMachine().this_week_number_sign()

        last_sunday = TimeMachine().last_sunday()
        end = TimeMachine().date_to_number(last_sunday)

        start_number = end - 7
        start = TimeMachine().number_to_system_date(start_number)

        clients = ClientsManager().list_current_clients()

        for client in clients:
            points = self.calculate_points_this_week(client)

            StreamManager().add_to_stream(
                client,
                "Activity",
                f"homework {week_sign};{points}",
                current_user
                )

        StreamManager().add_to_stream(
            "system",
            "Settle activity",
            week_sign,
            current_user
            )
