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

from nieszkolni_folder.curriculum_manager import CurriculumManager

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

    def display_questions_by_survey(self, survey_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT question_ids
                FROM nieszkolni_app_survey
                WHERE id = '{survey_id}'
                ''')

            question_ids_raw = cursor.fetchone()

            questions = []
            if question_ids_raw is not None:
                if question_ids_raw[0] != "":
                    question_ids = question_ids_raw[0].split(";")

                    for question_id in question_ids:
                        if question_id is not None:
                            if question_id != "":
                                question = self.display_question_simplified(question_id)
                                questions.append(question)

            return questions

    def display_question_simplified(self, question_id):
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

            return question

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

    def add_survey(
            self,
            title,
            content
            ):

        title = Cleaner().clean_quotation_marks(title)
        content = Cleaner().clean_quotation_marks(content)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_survey (
                title,
                content,
                question_ids
                )
                VALUES (
                '{title}',
                '{content}',
                ''
                )
                ''')

    def display_surveys(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                title,
                content,
                question_ids
                FROM nieszkolni_app_survey
                ''')

            surveys = cursor.fetchall()

            return surveys

    def display_survey(self, survey_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                title,
                content,
                question_ids
                FROM nieszkolni_app_survey
                WHERE id = '{survey_id}'
                ''')

            survey = cursor.fetchone()

            return survey

    def convert_ids(self, question_ids):
        results = []
        things = question_ids.split(";")
        for thing in things:
            if thing != "":
                results.append(thing)

        return results

    def add_question_to_survey(self, survey_id, question_id):
        survey = Survey.objects.get(id=survey_id)
        question_ids_entry = survey.question_ids
        question_ids = self.convert_ids(question_ids_entry)
        question_ids.append(question_id)
        question_ids_new_entry = ";".join(question_ids)
        survey.question_ids = question_ids_new_entry
        survey.save()

    def plan_survey(self, item):
        assignment = CurriculumManager().display_assignment(item)
        client = assignment[3]
        survey_id = assignment[16]

        survey = Survey.objects.get(id=survey_id)
        check = SurveyResponse.objects.filter(item=item).exists()

        if not check:
            question_ids_raw = survey.question_ids
            question_ids = self.convert_ids(question_ids_raw)

            for question_id in question_ids:

                response = SurveyResponse()
                response.stamp = TimeMachine().now_number()
                response.client = client
                response.response = ""
                response.survey_id = survey_id
                response.question_id = question_id
                response.response_id = 0
                response.item = item
                response.save()

    def take_survey(self, item):
        self.plan_survey(item)

        check = SurveyResponse.objects.filter(item=item, response="").exists()

        if check:
            survey = SurveyResponse.objects.filter(item=item, response="")
            question_reference = survey[0]
            question_id = question_reference.question_id
            question = SurveyQuestion.objects.get(id=question_id)

            option_ids_raw = question.option_ids
            option_ids = self.convert_ids(option_ids_raw)
            options = [SurveyOption.objects.get(id=uid) for uid in option_ids]

            total = SurveyResponse.objects.filter(item=item).count()
            awaiting = survey.count()
            count = total - awaiting + 1

            response_id = question_reference.id

            return (response_id, question, options, count, total)

    def respond(self, response, response_id):
        response = Cleaner().clean_quotation_marks(response)

        question = SurveyResponse.objects.get(id=response_id)
        question.response = response
        question.save()

    def display_responses(self, question_id):
        check = SurveyResponse.objects.filter(question_id=question_id).exists()

        if check:
            responses = SurveyResponse.objects.filter(question_id=question_id)
            return responses
