import os
import django

from django.db import connection

from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_app.models import Stream

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

    def get_conditions(self, client, date):
        date_number = TimeMachine().date_to_number(date)
        previous_sunday = TimeMachine().previous_sunday(date)
        following_sunday = TimeMachine().following_sunday(date)

        assignments = CurriculumManager().assignments_and_status_from_to(
                client,
                previous_sunday,
                following_sunday
                )

        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")
        po = StreamManager().count_po_from_to(
                client,
                previous_sunday,
                following_sunday
                )
        homework = StreamManager().find_command_from_to(
                client,
                "Homework",
                previous_sunday,
                following_sunday
                )
        homework_count = len([item.command for item in homework])
        stats = StreamManager().statistics_range(
                client,
                previous_sunday,
                following_sunday
                )
        duration = stats["duration"]
        flashcards_check = stats["study_days"]

        completed = []
        uncompleted = []

        for assignment in assignments:
            if assignment[2] not in no_submissions:
                deadline = assignment[1]
                completion_date = assignment[4]

                if completion_date > deadline:
                    uncompleted.append(assignment[0])

                elif completion_date == 0 and deadline < date_number:
                    uncompleted.append(assignment[0])

                else:
                    completed.append(assignment[0])

        uncompleted_count = len(uncompleted)

        conditions = {
            "uncompleted_count": uncompleted_count,
            "homework_count": homework_count,
            "po": po,
            "flashcards_check": flashcards_check,
            "duration": duration
            }

        return conditions

    def evaluate_conditions(self, conditions):
        uncompleted_count = conditions["uncompleted_count"]
        homework_count = conditions["homework_count"]
        po = conditions["po"]
        flashcards_check = conditions["flashcards_check"]
        duration = conditions["duration"]

        evaluation = {
            "minimum": False,
            "maximum": False,
            "attendance": False
            }

        if uncompleted_count == 0 and homework_count == 0:
            evaluation.update({"maximum": True})

        if po > 30 and flashcards_check > 2:
            evaluation.update({"minimum": True})

        if duration > 0:
            evaluation.update({"attendance": True})

        return evaluation

    def get_score(self, evaluation):
        no_homework = BackOfficeManager().display_option_by_command(
                "no_homework_ap"
                )
        full_homework = BackOfficeManager().display_option_by_command(
                "full_homework_ap"
                )
        main_homework = BackOfficeManager().display_option_by_command(
                "main_homework_ap"
                )

        minimum = evaluation["minimum"]
        maximum = evaluation["maximum"]
        attendance = evaluation["attendance"]

        score = 0

        if minimum is False:
            score = int(no_homework) if no_homework is not None else 0
        else:
            if maximum is True:
                score = int(full_homework) if full_homework is not None else 0
            else:
                score = int(main_homework) if main_homework is not None else 0

        if attendance is True and minimum is not False:
            score *= 2

        return score

    def calculate_points(self, client, date):
        conditions = self.get_conditions(client, date)
        evaluation = self.evaluate_conditions(conditions)
        score = self.get_score(evaluation)

        return score

    def get_points(self, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        rows = Stream.objects.filter(
            name=client,
            command="Activity",
            date_number__gte=start_number,
            date_number__lt=end_number
                )

        if not rows.exists():
            return 0
        else:
            entries = [row.value for row in rows]
            points = [
                Cleaner().convert_acitivty_points_entry(entry)
                for entry in entries
                ]

            score = sum(points)

            return score

    def get_points_last_week(self, client):
        last_sunday = TimeMachine().last_sunday()
        previous_sunday = TimeMachine().previous_sunday(last_sunday)
        last_sunday_number = TimeMachine().date_to_number(last_sunday)
        previous_sunday_number = TimeMachine().date_to_number(previous_sunday)

        rows = Stream.objects.filter(
            name=client,
            command="Activity",
            date_number__gte=previous_sunday_number,
            date_number__lt=last_sunday_number
                )

        if not rows.exists():
            return 0
        else:
            entries = [row.value for row in rows]
            points = [
                Cleaner().convert_acitivty_points_entry(entry)[1]
                for entry in entries
                ]

            score = sum(points)

            return score

    def get_points_over_lifetime(self, client):
        lessons = Stream.objects.filter(name=client, command="Duration")
        if not lessons.exists():
            return None

        first_lesson = lessons.order_by("date_number")[0]
        start = first_lesson.date
        sundays = TimeMachine().display_sundays_range(start)

        results = []

        for sunday in sundays:
            conditions = self.get_conditions(client, sunday[1])
            week = TimeMachine().number_to_week_number_sign(sunday[0])
            conditions.update({"week": week})

            start_sunday = TimeMachine().number_to_system_date(sunday[0])
            end_sunday = TimeMachine().number_to_system_date(sunday[0] + 7)
            points = StreamManager().activity_points_by_client_week(
                client,
                "homework",
                start_sunday,
                end_sunday
                    )

            points = sum(points)
            conditions.update({"activity_points": points})

            results.append(conditions)

        return results

    def get_points_over_lifetime_lists(self, client):
        data = self.get_points_over_lifetime(client)

        if data is None:
            return ([0], [0])

        activity_points = [x["activity_points"] for x in data]
        weeks = [x["week"] for x in data]

        activity_points.reverse()
        weeks.reverse()

        result = (activity_points, weeks)

        return result

    def get_points_over_lifetime_total(self, client):
        data = self.get_points_over_lifetime(client)

        if data is None:
            return 0

        activity_points = [x["activity_points"] for x in data]
        activity_points = sum(activity_points)

        return activity_points

    def get_points_last_week_per_client(self):
        last_sunday = TimeMachine().last_sunday()
        previous_sunday = TimeMachine().previous_sunday(last_sunday)
        clients = ClientsManager().list_current_clients()
        results = []

        for client in clients:
            coach = ClientsManager().get_coach_by_client(client)
            conditions = self.get_conditions(client, last_sunday)

            points = StreamManager().activity_points_by_client_week(
                client,
                "homework",
                previous_sunday,
                last_sunday
                    )

            points = sum(points)

            conditions.update({"activity_points": points})
            conditions.update({"client": client})
            conditions.update({"coach": coach})

            results.append(conditions)

        return results

    def calculate_points_this_week(self, client):
        today = TimeMachine().today_number()
        last_sunday = TimeMachine().last_sunday()
        previous_sunday = TimeMachine().previous_sunday(last_sunday)

        assignments = CurriculumManager().assignments_and_status_from_to(
                client,
                previous_sunday,
                last_sunday
                )

        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")
        po = StreamManager().count_po_from_to(client, previous_sunday, last_sunday)
        homework = StreamManager().find_command_from_to(
                client,
                "Homework",
                previous_sunday,
                last_sunday
                )
        homework_count = len([item.command for item in homework])
        stats = StreamManager().statistics_range(
                client,
                previous_sunday,
                last_sunday
                )
        duration = stats["duration"]  # only specified time
        flashcards_check = stats["study_days"]  # only specified time

        no_homework = BackOfficeManager().display_option_by_command("no_homework_ap")
        full_homework = BackOfficeManager().display_option_by_command("full_homework_ap")
        main_homework = BackOfficeManager().display_option_by_command("main_homework_ap")

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

        uncompleted_count = len(uncompleted)

        if uncompleted_count == 0 and homework_count == 0:
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
            score = int(no_homework) if no_homework is not None else 0
        else:
            if maximum is True:
                score = int(full_homework) if full_homework is not None else 0
            else:
                score = int(main_homework) if main_homework is not None else 0

        if attendance is True and minimum is not False:
            score *= 2

        return score

    def get_uncompleted_assignments_list(self, client, date=None):
        if date is None:
            date = TimeMachine().today()
        date_number = TimeMachine().date_to_number(date)
        last_sunday = TimeMachine().previous_sunday(date)
        previous_sunday = TimeMachine().previous_sunday(last_sunday)
        following_sunday = TimeMachine().following_sunday(date)

        assignments = CurriculumManager().assignments_and_status_from_to(
                client,
                previous_sunday,
                following_sunday
                )

        no_submissions = KnowledgeManager().display_list_of_prompts("no_submission")

        completed = []
        uncompleted = []

        for assignment in assignments:
            if assignment[2] not in no_submissions:
                deadline = assignment[1]
                completion_date = assignment[4]

                if completion_date > deadline:
                    uncompleted.append(assignment[0])

                elif completion_date == 0 and deadline < date_number:
                    uncompleted.append(assignment[0])

                else:
                    completed.append(assignment[0])

        uncompleted = [x for x in assignments if x[0] in uncompleted]

        return uncompleted

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
            last_sunday = TimeMachine().last_sunday()
            last_sunday_number = TimeMachine().date_to_number(last_sunday)

            lessons = Stream.objects.filter(
                    name=client,
                    command="Duration",
                    date_number__lte=last_sunday_number)

            if lessons.exists():
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
