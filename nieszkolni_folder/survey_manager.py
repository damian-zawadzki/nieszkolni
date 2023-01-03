import os
import django
from django.db import connection

from nieszkolni_app.models import Survey
from nieszkolni_app.models import SurveyQuestion
from nieszkolni_app.models import SurveyOption
from nieszkolni_app.models import SurveyResponse

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.sentence_manager import SentenceManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class SurveyManager:
    def __init__(self):
        pass

    def add_option(self, option, option_value):
        option = Cleaner().clean_quotation_marks(option)
        option_value = Cleaner().clean_quotation_marks(option_value)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_surveyoption (
                option,
                option_value
                )
                VALUES (
                '{option}',
                '{option_value}'
                )
                ''')

    def display_options(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                option,
                option_value
                FROM nieszkolni_app_surveyoption
                ''')

            options = cursor.fetchall()

            return options

    def display_option(self, option_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                option,
                option_value
                FROM nieszkolni_app_surveyoption
                WHERE id = '{option_id}'
                ''')

            option = cursor.fetchone()

            return option

    def add_question(
            self,
            question,
            question_type,
            option_ids,
            action
            ):

        question = Cleaner().clean_quotation_marks(question)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_surveyquestion (
                question,
                question_type,
                option_ids,
                action
                )
                VALUES (
                '{question}',
                '{question_type}',
                '{option_ids}',
                '{action}'
                )
                ''')

    def display_questions(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                question,
                question_type,
                option_ids,
                action
                FROM nieszkolni_app_surveyquestion
                ''')

            questions = cursor.fetchall()

            return questions

    def display_question(self, question_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                question,
                question_type,
                option_ids,
                action
                FROM nieszkolni_app_surveyquestion
                WHERE id = '{question_id}'
                ''')

            question = cursor.fetchone()

            options = []
            if question is not None:
                if question[3] != "":
                    option_ids = question[3].split(";")

                    for option_id in option_ids:
                        option = self.display_option(option_id)
                        options.append(option)

            return (question, options)