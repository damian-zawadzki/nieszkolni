import os
import django
from django.db import connection
from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class CurriculumManager:
    def __init__(self):
        today_pattern = "%Y-%m-%d"

    def add_curriculum(
            self,
            item,
            deadline,
            name,
            component_id,
            component_type,
            assignment_type,
            title,
            content,
            matrix,
            resources,
            conditions,
            reference
            ):

        content = Cleaner().clean_quotation_marks(content)
        conditions = Cleaner().clean_quotation_marks(conditions)

        with connection.cursor() as cursor:
            try:
                deadline = TimeMachine().american_to_system_date(deadline)
            except Exception as e:
                print(e)

            deadline_number = TimeMachine().date_to_number(deadline)
            default_status = 'uncompleted'
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_curriculum (
                item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status,
                completion_stamp,
                completion_date,
                submitting_user,
                conditions,
                reference
                ) VALUES (
                '{item}',
                '{deadline}',
                '{deadline_number}',
                '{name}',
                '{component_id}',
                '{component_type}',
                '{assignment_type}',
                '{title}',
                '{content}',
                '{matrix}',
                '{resources}',
                '{default_status}',
                0,
                0,
                '',
                '{conditions}',
                {reference}
                ) ON CONFLICT (item)
                DO NOTHING
                ''')

    def display_uncompleted_assignments(self, name):
        today_number = TimeMachine().today_number()
        display_limit = today_number + 7

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status
                FROM nieszkolni_app_curriculum
                WHERE name = '{name}' AND status != 'completed'
                AND deadline_number <= '{display_limit}'
                ''')

            uncompleted_assignments = cursor.fetchall()
            uncompleted_assignments.sort(key=lambda item: item[2])

        return uncompleted_assignments

    def display_completed_assignments(self, name):
        today_number = TimeMachine().today_number()
        display_limit = today_number - 7

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status
                FROM nieszkolni_app_curriculum
                WHERE name = '{name}'
                AND status == 'completed'
                AND completion_date >= {display_limit}
                ''')

            completed_assignments = cursor.fetchall()
            completed_assignments.sort(key=lambda item: item[2])

        return completed_assignments

    def display_assignment(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status
                FROM nieszkolni_app_curriculum
                WHERE item = {item}
                ''')

            assignment = cursor.fetchall()

        return assignment[0]

    def change_status_to_completed(self, item, submitting_user):
        now_number = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_curriculum
                SET status = 'completed',
                completion_stamp = {now_number},
                completion_date = {today_number},
                submitting_user = '{submitting_user}'
                WHERE item = {item}
                ''')

    def change_status_to_uncompleted(self, item, submitting_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_curriculum
                SET status = 'uncompleted',
                completion_stamp = 0,
                completion_date = 0,
                submitting_user = '{submitting_user}'
                WHERE item = {item}
                ''')

    def display_all_assignments(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status
                FROM nieszkolni_app_curriculum
                ''')

            all_assignments = cursor.fetchall()
            all_assignments.sort(key=lambda item: item[2])

        return all_assignments

    def display_assignments_for_student(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT item,
                deadline_text,
                deadline_number,
                name,
                component_id,
                component_type,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                status
                FROM nieszkolni_app_curriculum
                WHERE name = '{name}'
                ''')

            assignments = cursor.fetchall()
            assignments.sort(key=lambda item: item[2])

        return assignments

    def next_item(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT MAX(item)
                FROM nieszkolni_app_curriculum
                ''')

            last_item = cursor.fetchone()
            next_item = last_item[0] + 1

            return next_item

    def remove_curriculum(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_curriculum
                WHERE item = {item}
                ''')

    def check_position_in_library(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                l.position_number,
                l.title,
                l.wordcount,
                l.link
                FROM nieszkolni_app_library l
                INNER JOIN nieszkolni_app_curriculum c
                ON c.reference = l.position_number
                WHERE c.item = {item}
                ''')

            position = cursor.fetchone()

            return position

    def check_assignment_type(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                assignment_type
                FROM nieszkolni_app_curriculum
                WHERE item = {item}
                ''')

            assignment_type = cursor.fetchone()
            assignment_type = assignment_type[0]

            return assignment_type

    def add_module(
            self,
            component_id,
            component_type,
            title,
            content,
            resources,
            conditions
            ):

        title = Cleaner().clean_quotation_marks(title)
        content = Cleaner().clean_quotation_marks(content)
        resources = Cleaner().clean_quotation_marks(resources)
        conditions = Cleaner().clean_quotation_marks(conditions)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_module (
                component_id,
                component_type,
                title,
                content,
                resources,
                conditions
                )
                VALUES (
                '{component_id}',
                '{component_type}',
                '{title}',
                '{content}',
                '{resources}',
                '{conditions}'
                )
                ''')

    def display_modules(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                component_id,
                component_type,
                title,
                content,
                resources,
                conditions
                FROM nieszkolni_app_module
                ''')

            modules = cursor.fetchall()

            return modules

    def display_module(self, component_id):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                component_id,
                component_type,
                title,
                content,
                resources,
                conditions
                FROM nieszkolni_app_module
                WHERE component_id = '{component_id}'
                ''')

            module = cursor.fetchone()

            return module

    def display_components(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                component_id
                FROM nieszkolni_app_module
                ''')

            components = cursor.fetchall()

            return components

    def add_matrix(
            self,
            component_id,
            matrix,
            limit_number
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_matrix (
                component_id,
                matrix,
                limit_number
                )
                VALUES (
                '{component_id}',
                '{matrix}',
                '{limit_number}'
                )
                ''')

    def display_matrix(self, matrix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                component_id,
                matrix,
                limit_number
                FROM nieszkolni_app_matrix
                WHERE matrix = '{matrix}'
                ORDER BY limit_number ASC
                ''')

            rows = cursor.fetchall()

            modules = []
            for row in rows:
                entry = dict()
                entry.update({
                    "component_id": row[0],
                    "matrix": row[1],
                    "limit_number": row[2]
                    })
                modules.append(entry)

            return modules

    def display_matrices(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT
                matrix
                FROM nieszkolni_app_matrix
                ''')

            matrices = cursor.fetchall()

            return matrices