import os
import django
from django.db import connection
from nieszkolni_app.models import Question
from nieszkolni_app.models import Assessment
from nieszkolni_app.models import Quiz
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class QuizManager:
    def __init__(self):
        pass

    # Questions
    def add_question(
            self,
            description,
            question,
            answer_a,
            answer_b,
            answer_c,
            answer_d,
            correct_answer,
            question_type
            ):

        description = Cleaner().clean_quotation_marks(description)
        question = Cleaner().clean_quotation_marks(question)
        answer_a = Cleaner().clean_quotation_marks(answer_a)
        answer_b = Cleaner().clean_quotation_marks(answer_b)
        answer_c = Cleaner().clean_quotation_marks(answer_c)
        answer_d = Cleaner().clean_quotation_marks(answer_d)
        correct_answer = Cleaner().clean_quotation_marks(correct_answer)    

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_question (
                description,
                question,
                answer_a,
                answer_b,
                answer_c,
                answer_d,
                correct_answer,
                question_type
                )
                VALUES (
                '{description}',
                '{question}',
                '{answer_a}',
                '{answer_b}',
                '{answer_c}',
                '{answer_d}',
                '{correct_answer}',
                '{question_type}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def update_question(
            self,
            description,
            question,
            answer_a,
            answer_b,
            answer_c,
            answer_d,
            correct_answer,
            question_type,
            question_id
            ):

        description = Cleaner().clean_quotation_marks(description)
        question = Cleaner().clean_quotation_marks(question)
        answer_a = Cleaner().clean_quotation_marks(answer_a)
        answer_b = Cleaner().clean_quotation_marks(answer_b)
        answer_c = Cleaner().clean_quotation_marks(answer_c)
        answer_d = Cleaner().clean_quotation_marks(answer_d)
        correct_answer = Cleaner().clean_quotation_marks(correct_answer)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_question
                SET
                description = '{description}',
                question = '{question}',
                answer_a = '{answer_a}',
                answer_b = '{answer_b}',
                answer_c = '{answer_c}',
                answer_d = '{answer_d}',
                correct_answer = '{correct_answer}',
                question_type = '{question_type}'
                WHERE question_id = {question_id}
                ''')

    def display_questions(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                description,
                question,
                answer_a,
                answer_b,
                answer_c,
                answer_d,
                correct_answer,
                question_type,
                question_id
                FROM nieszkolni_app_question
                ''')

            questions = cursor.fetchall()

            return questions

    def display_question(self, question_id):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                description,
                question,
                answer_a,
                answer_b,
                answer_c,
                answer_d,
                correct_answer,
                question_type,
                question_id
                FROM nieszkolni_app_question
                WHERE question_id = {question_id}
                ''')

            question = cursor.fetchone()

            return question

    def display_question_type(self, question_id):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT question_type
                FROM nieszkolni_app_question
                WHERE question_id = '{question_id}'
                ''')

            question_type = cursor.fetchone()

            return question_type[0]

    # Collections
    def add_collection(
            self,
            collection_name,
            collection_id,
            question_id
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_collection (
                collection_name,
                collection_id,
                question_id
                )
                VALUES (
                '{collection_name}',
                {collection_id},
                {question_id}
                )
                ''')

    def display_next_collection_id(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT collection_id
                FROM nieszkolni_app_collection
                ORDER BY collection_id DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                collection_id = 100000
            else:
                collection_id = data[0] + 1

            return collection_id

    def display_collection_ids(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT collection_id, collection_name
                FROM nieszkolni_app_collection
                ''')

            collection_ids = cursor.fetchall()

            return collection_ids

    def display_collection_name(self, collection_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT collection_name
                FROM nieszkolni_app_collection
                WHERE collection_id = '{collection_id}'
                ''')

            collection_name = cursor.fetchone()

            if collection_name is not None:
                collection_name = collection_name[0]

            return collection_name

    def display_collection(self, collection_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                c.question_id,
                q.question
                FROM nieszkolni_app_collection AS c
                INNER JOIN nieszkolni_app_question AS q ON q.question_id = c.question_id
                WHERE c.collection_id = '{collection_id}'
                ''')

            questions = cursor.fetchall()

            return questions

    # Assessment
    # We register a quiz.
    def add_quiz(
            self,
            client,
            item
            ):

        quiz_id = self.display_next_quiz_id()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_assessment (
                quiz_id,
                client,
                status,
                item
                )
                VALUES (
                '{quiz_id}',
                '{client}',
                'registered',
                '{item}'
                )
                ON CONFLICT (quiz_id)
                DO NOTHING
                ''')

        return quiz_id

    # Quizzes
    # We add questions to quizzes
    def add_question_to_quiz(
            self,
            quiz_id,
            question_id,
            client,
            collection_name,
            collection_id,
            quiz_question_id
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_quiz (
                quiz_id,
                question_id,
                client,
                answer,
                result,
                date_number,
                status,
                quiz_question_id,
                collection_name,
                collection_id
                )
                VALUES (
                '{quiz_id}',
                '{question_id}',
                '{client}',
                '',
                '',
                '0',
                'generated',
                '{quiz_question_id}',
                '{collection_name}',
                '{collection_id}'
                )
                ''')

    def update_quiz_status(self, quiz_id, status):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_assessment
                SET status = '{status}'
                WHERE quiz_id = {quiz_id}
                ''')

    def display_next_quiz_id(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT quiz_id
                FROM nieszkolni_app_assessment
                ORDER BY quiz_id DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                quiz_id = 100000
            else:
                quiz_id = data[0] + 1

            return quiz_id

    # Planning quizzes
    def plan_quiz(
            self,
            client,
            item,
            reference
            ):

        # Register a quiz
        quiz_id = self.add_quiz(client, item)

        # Find questions based on reference in module
        rows = self.display_collection(reference)

        # Add questions based on collection
        collection_id = reference
        collection_name = self.display_collection_name(reference)
        position = 0

        for row in rows:

            question_id = row[0]

            position_number = f"{position:02d}"
            quiz_question_id = f"{quiz_id}{position_number}"

            self.add_question_to_quiz(
                quiz_id,
                question_id,
                client,
                collection_name,
                collection_id,
                quiz_question_id
                )

            position += 1

        self.update_quiz_status(quiz_id, "planned")

    # Taking a quiz

    def find_quiz_id_by_item(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT quiz_id
                FROM nieszkolni_app_assessment
                WHERE item = '{item}'
                ''')

            quiz_id = cursor.fetchone()

            if quiz_id is not None:
                quiz_id = quiz_id[0]

            return quiz_id

    def display_next_generated_question(self, quiz_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT quiz_question_id
                FROM nieszkolni_app_quiz
                WHERE quiz_id = '{quiz_id}'
                AND status = 'generated'
                ORDER BY quiz_question_id ASC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                quiz_question_id = f"{quiz_id}00"
            else:
                quiz_question_id = data[0]

            return quiz_question_id

    def display_quiz(self, quiz_question_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                qz.quiz_id,
                qz.question_id,
                qz.client,
                qz.answer,
                qz.result,
                qz.date_number,
                qs.question,
                qs.description,
                qs.answer_a,
                qs.answer_b,
                qs.answer_c,
                qs.answer_d,
                qs.correct_answer
                FROM nieszkolni_app_quiz AS qz
                INNER JOIN nieszkolni_app_question AS qs ON qs.question_id = qz.question_id
                WHERE qz.quiz_question_id = '{quiz_question_id}'
                AND status = 'generated'
                ORDER BY RAND()
                LIMIT 1
                ''')

            quiz = cursor.fetchone()

            return quiz

    def display_number_of_questions(self, quiz_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (quiz_id)
                FROM nieszkolni_app_quiz
                WHERE quiz_id = '{quiz_id}'
                AND status = 'generated'
                ''')

            number_of_questions = cursor.fetchone()

            return number_of_questions[0]

    def display_result(self, quiz_id):

        correct = 0

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(result)
                FROM nieszkolni_app_quiz
                WHERE quiz_id = '{quiz_id}'
                AND result = 'correct'
                ''')

            correct_result = cursor.fetchone()

            if correct_result is None:
                correct = 0
            else:
                correct = correct_result[0]

        incorrect = 0

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(result)
                FROM nieszkolni_app_quiz
                WHERE quiz_id = '{quiz_id}'
                AND result = 'incorrect'
                ''')

            incorrect_result = cursor.fetchone()

            if incorrect_result is None:
                incorrect = 0
            else:
                incorrect = incorrect_result[0]

        result_raw = correct/(correct + incorrect) * 100
        result = re.search(r"\d{1,3}", str(result_raw)).group()

        return result

    def record_answer(
            self,
            quiz_id,
            question_id,
            client,
            answer,
            result
            ):

        date_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_quiz
                SET
                answer = '{answer}',
                result = '{result}',
                date_number = '{date_number}',
                status = 'answered'
                WHERE quiz_id = {quiz_id}
                AND question_id = {question_id}
                AND client = '{client}'
                ''')


# to be sorted

    def display_quiz_ids(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT quiz_id, client
                FROM nieszkolni_app_assessment
                ''')

            quiz_ids = cursor.fetchall()

            return quiz_ids

    def display_quiz_status(self, quiz_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                quiz_id,
                status
                FROM nieszkolni_app_assessment
                WHERE quiz_id = {quiz_id}
                ''')

            quiz = cursor.fetchone()

            return quiz

    def display_quiz_ids_per_client(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT quiz_id, collection_name, collection_id
                FROM nieszkolni_app_quiz
                WHERE client = '{client}'
                ''')

            quiz_ids = cursor.fetchall()

            return quiz_ids

    def display_registered_quiz_ids_per_client(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT
                quiz_id
                FROM nieszkolni_app_assessment
                WHERE client = '{client}'
                AND status = 'registered'
                ''')

            quiz_ids = cursor.fetchall()

            return quiz_ids

    def questions_per_quiz_plus_1(self, quiz_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(quiz_id)
                FROM nieszkolni_app_quiz
                WHERE quiz_id = {quiz_id}
                ''')

            data = cursor.fetchone()
            if data is None:
                questions_per_quiz_plus_1 = 1
            else:
                questions_per_quiz = data[0] 
                questions_per_quiz_plus_1 = questions_per_quiz_plus_1 = 1

            return questions_per_quiz_plus_1

    def display_quizzes(self, client, quiz_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                qz.quiz_question_id,
                qz.quiz_id,
                qz.question_id,
                qz.client,
                qz.answer,
                qz.result,
                qz.date_number,
                qz.status,
                qz.collection_name,
                qz.collection_id,
                qs.question
                FROM nieszkolni_app_quiz AS qz
                INNER JOIN nieszkolni_app_question AS qs ON qs.question_id = qz.question_id
                WHERE qz.client = '{client}'
                AND qz.quiz_id = {quiz_id}
                ''')

            quizzes = cursor.fetchall()

            return quizzes

    def remove_question_from_quiz(self, quiz_id, question_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_quiz
                WHERE quiz_id = '{quiz_id}'
                AND question_id = {question_id}
                ''')

    def display_planned_quizzes_per_student(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT quiz_id
                FROM nieszkolni_app_assessment
                WHERE client = '{client}'
                AND status = 'planned'
                ''')

            quizzes = cursor.fetchall()

            return quizzes


