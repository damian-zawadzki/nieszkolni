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

        if reference == "":
            reference = 0

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
                )
                VALUES (
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
                )
                ON CONFLICT (item)
                DO NOTHING
                ''')

    def display_uncompleted_assignments(self, name):
        today_number = TimeMachine().today_number()
        this_sunday = TimeMachine().this_sunday()
        display_limit = TimeMachine().date_to_number(this_sunday)

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
                ORDER BY deadline_number ASC
                ''')

            uncompleted_assignments = cursor.fetchall()

        return uncompleted_assignments

    def display_completed_assignments(self, name):
        today_number = TimeMachine().today_number()
        last_sunday = TimeMachine().last_sunday()
        last_sunday_number = TimeMachine().date_to_number(last_sunday)
        display_limit = last_sunday_number - 7

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
                AND status = 'completed'
                AND completion_date >= '{display_limit}'
                ORDER BY deadline_number DESC
                ''')

            completed_assignments = cursor.fetchall()

        return completed_assignments

    def display_assignment(self, item):
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
                status,
                conditions,
                completion_stamp,
                completion_date,
                submitting_user,
                reference
                FROM nieszkolni_app_curriculum
                WHERE item = '{item}'
                ''')

            assignment = cursor.fetchone()

        return assignment

    def display_assignment_status(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT status
                FROM nieszkolni_app_curriculum
                WHERE item = '{item}'
                ''')

            assignment_status = cursor.fetchone()

        return assignment_status[0]

    def display_assignment_status_by_component_id(self, component_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT status
                FROM nieszkolni_app_curriculum
                WHERE component_id LIKE '{component_id}%'
                ''')

            rows = cursor.fetchall()

            items = [row[0] for row in rows]

            if items.count("completed") == len(items):
                status = "completed"
            else:
                status = "uncompleted"

            return status

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

    def change_status_to_fake_completed(self, item, submitting_user):
        now_number = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_curriculum
                SET status = 'fake_completed',
                completion_stamp = '{now_number}',
                completion_date = '{today_number}',
                submitting_user = '{submitting_user}'
                WHERE item = '{item}'
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

            if last_item[0] is None:
                next_item = 1000000
            else:
                next_item = last_item[0] + 1

            return next_item

    def remove_curriculum(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_curriculum
                WHERE item = '{item}'
                ''')

    def remove_curricula(self, client, component_id, deadline):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_curriculum
                WHERE name = '{client}'
                AND component_id = '{component_id}'
                AND deadline_number = '{deadline}'
                ''')

    def display_expiration_date(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT deadline_number
                FROM nieszkolni_app_curriculum
                WHERE name = '{client}'
                AND status = 'uncompleted'
                ORDER BY deadline_number DESC
                LIMIT 1
                ''')

            date_raw = cursor.fetchone()

            if date_raw is not None:
                date = TimeMachine().number_to_system_date(date_raw[0])
                return (client, date_raw[0], date)
            else:
                return (client, 0, "expired")

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
                WHERE c.item = '{item}'
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

    def assignments_from_to(self, client, start, end, status):
        start_number = TimeMachine().date_to_number(start)
        end_number = TimeMachine().date_to_number(end)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT assignment_type
                FROM nieszkolni_app_curriculum
                WHERE status = '{status}'
                AND name = '{client}'
                AND deadline_number > '{start_number}'
                AND deadline_number <= '{end_number}'
                ''')

            assignments = cursor.fetchall()

            return assignments

    def assignments_and_status_from_to(self, client, start, end):
        start_number = TimeMachine().date_to_number(start)
        end_number = TimeMachine().date_to_number(end)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                item,
                deadline_number,
                assignment_type,
                status,
                completion_date
                FROM nieszkolni_app_curriculum
                WHERE name = '{client}'
                AND deadline_number > '{start_number}'
                AND deadline_number <= '{end_number}'
                ''')

            assignments = cursor.fetchall()

            return assignments

    def component_id_to_component(self, component_id):
        component_raw = re.search(r"\w.+_", component_id).group()
        component = re.sub("_", "", component_raw)

        return component

    def add_module(
            self,
            component_id,
            component_type,
            title,
            content,
            resources,
            conditions,
            reference
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
                conditions,
                reference
                )
                VALUES (
                '{component_id}',
                '{component_type}',
                '{title}',
                '{content}',
                '{resources}',
                '{conditions}',
                {reference}
                )
                ''')

    def update_module(
            self,
            component_id,
            component_type,
            title,
            content,
            resources,
            conditions,
            reference
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_module
                SET
                component_type = '{component_type}',
                title = '{title}',
                content = '{content}',
                resources = '{resources}',
                conditions = '{conditions}',
                reference = '{reference}'
                WHERE component_id = '{component_id}'
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
                conditions,
                reference
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
                conditions,
                reference
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

    def update_matrix(
            self,
            new_matrix,
            old_matrix
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_matrix
                SET matrix = '{new_matrix}'
                WHERE matrix = '{old_matrix}'
                ''')

    def display_matrix(self, matrix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                component_id,
                matrix,
                limit_number,
                id
                FROM nieszkolni_app_matrix
                WHERE matrix = '{matrix}'
                ORDER BY
                limit_number ASC, 
                component_id ASC
                ''')

            rows = cursor.fetchall()
            modules = []
            for row in rows:
                entry = dict()
                entry.update({
                    "component_id": row[0],
                    "matrix": row[1],
                    "limit_number": row[2],
                    "matrix_id": row[3]
                    })
                modules.append(entry)

            return modules

    def display_matrices(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT matrix
                FROM nieszkolni_app_matrix
                ''')

            matrices = cursor.fetchall()

            return matrices

    def add_id_prefix(self, matrix, next_id_prefix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_prefix (
                matrix,
                id_prefix
                )
                VALUES (
                '{matrix}',
                '{next_id_prefix}'
                )
                ''')

    def next_id_prefix(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT id_prefix
                FROM nieszkolni_app_prefix
                ORDER BY id_prefix DESC
                LIMIT 1
                ''')

            id_prefix = cursor.fetchone()

            if id_prefix is None:
                next_id_prefix = 100
            else:
                next_id_prefix = int(id_prefix[0]) + 1

            return next_id_prefix

    def display_prefixes(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT matrix, id_prefix
                FROM nieszkolni_app_prefix
                ORDER BY id_prefix ASC
                ''')

            prefixes = cursor.fetchall()

            return prefixes

    def display_prefix_by_matrix(self, matrix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT id_prefix
                FROM nieszkolni_app_prefix
                WHERE matrix = '{matrix}'
                ''')

            data = cursor.fetchone()

            if data is not None:
                id_prefix = data[0]
            else:
                id_prefix = None

            return id_prefix

    def change_matrix_name(self, matrix, id_prefix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_prefix
                SET matrix = '{matrix}'
                WHERE id_prefix = '{id_prefix}'
                ''')

    def remove_module_from_matrix(self, matrix, component_id, limit_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_matrix
                WHERE matrix = '{matrix}'
                AND component_id = '{component_id}'
                AND limit_number = '{limit_number}'
                ''')

    def next_id_suffix(self, component, id_prefix):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT component_id
                FROM nieszkolni_app_module
                WHERE (component_id LIKE '{component}_{id_prefix}%')
                ORDER BY component_id DESC
                LIMIT 1
                ''')

            id_suffix = cursor.fetchone()
            print(id_suffix)

            if id_suffix is None:
                next_id_suffix = "01"
            else:
                data_raw = id_suffix[0]
                data = re.sub(f"{component}_{id_prefix}", "", data_raw)
                data = int(data)
                data = data + 1
                next_id_suffix = f"{data:02d}"

            return next_id_suffix