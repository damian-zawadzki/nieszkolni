import os
import django
import re
from django.db import connection

from nieszkolni_app.models import Submission

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.wordcounter import Wordcounter
from nieszkolni_folder.cleaner import Cleaner
from nieszkolni_folder.text_analysis import TextAnalysis

from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.challenge_manager import ChallengeManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class SubmissionManager:
    def __init__(self):
        pass

    def find_landing_page(self, item):
        conditions = CurriculumManager().display_assignment_conditions(item)
        activity_points = ChallengeManager().display_reward_by_item(item)
        activity_points = activity_points if activity_points is not None else 0

        if conditions == "challenge":
            page = "applause"

        else:
            page = "campus"

        return (page, activity_points)

    def run_submission(
            self,
            item,
            client,
            assignment_type,
            title,
            content,
            current_user
            ):

        page_object = self.find_landing_page(item)
        page = page_object[0]
        activity_points = page_object[1]

        try:
            commands = {
                "essay": "AV",
                "assignment": "AV",
                "wordfinder": "WF"
                }

            self.add_submission(
                        item,
                        client,
                        assignment_type,
                        title,
                        content
                        )

            CurriculumManager().change_status_to_completed(item, current_user)

            wordcount = Wordcounter(content).counter()
            linecount = Wordcounter(content).linecounter()
            command = commands.get(assignment_type)

            if command == "AV":
                value = wordcount
            else:
                value = linecount

            StreamManager().add_to_stream(client, command, value, current_user)

            if page == "applause":
                output = (
                        "SUCCESS",
                        "Assignment submitted",
                        page,
                        activity_points
                        )
            else:
                output = (
                        "SUCCESS",
                        "Assignment submitted",
                        page,
                        activity_points
                        )

            return output

        except Exception as e:

            if page == "applause":
                output = (
                        "ERROR",
                        "Assignment could not be submitted",
                        page,
                        activity_points
                        )
            else:
                output = (
                        "ERROR",
                        "Assignment could not be submitted",
                        page,
                        activity_points
                        )

            return output

    def add_submission(
            self,
            item,
            name,
            assignment_type,
            title,
            content
            ):

        stamp = TimeMachine().now_number()
        date_number = TimeMachine().today_number()
        date = TimeMachine().today()
        content = Cleaner().clean_quotation_marks(content)
        wordcount = Wordcounter(content).counter()
        status = "submitted"

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_submission (
                stamp,
                date_number,
                date,
                item,
                name,
                assignment_type,
                title,
                content,
                wordcount,
                status,
                reviewed_content,
                flagged_content,
                analysis,
                minor_errors,
                major_errors,
                reviewing_user,
                revision_date,
                conditions,
                comment,
                grade
                )
                VALUES (
                '{stamp}',
                '{date_number}',
                '{date}',
                '{item}',
                '{name}',
                '{assignment_type}',
                '{title}',
                '{content}',
                '{wordcount}',
                '{status}',
                '{content}',
                '',
                '',
                0,
                0,
                '',
                0,
                '',
                '',
                ''
                )
                ''')

    def display_students_assignments_limited(self, name):
        today_number = TimeMachine().today_number()
        limit = today_number - 30

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT date, title, content, wordcount, unique_id
                FROM nieszkolni_app_submission
                WHERE name = '{name}'
                AND date_number > '{limit}'
                ORDER BY date DESC
                ''')

            submissions = cursor.fetchall()

            return submissions

    def display_students_assignment(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                date,
                title,
                content,
                wordcount,
                unique_id,
                flagged_content,
                grade,
                major_errors,
                minor_errors,
                status,
                assignment_type,
                item
                FROM nieszkolni_app_submission
                WHERE unique_id = {unique_id}
                ''')

            submission = cursor.fetchone()

            return submission

    def assignments_to_grade(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT date, name, title, reviewed_content, unique_id
                FROM nieszkolni_app_submission
                WHERE (status = 'submitted'
                OR status = '')
                AND (assignment_type = 'essay'
                OR assignment_type = 'assignment')
                ''')

            essays = cursor.fetchall()

            return essays

    def display_assignment(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT s.date, s.name, s.title,
                CASE
                    WHEN s.reviewed_content = ''
                    THEN s.content
                    ELSE s.reviewed_content
                END AS reviewed_content,
                s.status, s.unique_id, c.conditions, s.comment
                FROM nieszkolni_app_submission s
                INNER JOIN nieszkolni_app_curriculum c
                ON s.item = c.item
                WHERE s.unique_id = {unique_id}
                ''')

            assignment = cursor.fetchone()
            print(assignment)
            return assignment

    def grade_assignment(
            self,
            unique_id,
            reviewed_content,
            reviewing_user,
            conditions,
            comment,
            grade
            ):

        reviewed_content = Cleaner().clean_quotation_marks(reviewed_content)
        flagged_content = TextAnalysis(reviewed_content).convert_to_flagged_text()

        analysis = str(TextAnalysis(reviewed_content).find_marks()).replace("'", '"')
        minor_errors = TextAnalysis(reviewed_content).calculate_errors("minor")
        major_errors = TextAnalysis(reviewed_content).calculate_errors("major")
        conditions = Cleaner().clean_quotation_marks(conditions)
        comment = Cleaner().clean_quotation_marks(comment)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_submission
                SET reviewed_content = '{reviewed_content}',
                reviewing_user = '{reviewing_user}',
                flagged_content = '{flagged_content}',
                analysis = '{analysis}',
                minor_errors = {minor_errors},
                major_errors = {major_errors},
                conditions = '{conditions}',
                comment = '{comment}',
                grade = '{grade}'
                WHERE unique_id = {unique_id}
                ''')

    def mark_as_graded(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_submission
                SET status = 'graded'
                WHERE unique_id = {unique_id}
                ''')

    def download_graded_assignments(self, start_date, end_date):
        start = TimeMachine().date_to_number(start_date)
        end = TimeMachine().date_to_number(end_date)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
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
                grade,
                assignment_type
                FROM nieszkolni_app_submission
                WHERE status = 'graded'
                AND date_number >= {start}
                AND date_number <= {end}
                ''')

            assignments = cursor.fetchall()

        return assignments
