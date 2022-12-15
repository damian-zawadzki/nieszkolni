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


class RatingManager:
    def __init__(self):
        pass

    def add_rating(
            self,
            client,
            category,
            position,
            rating
            ):

        date_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_rating (
                date_number,
                client,
                category,
                position,
                rating
                )
                VALUES (
                '{date_number}',
                '{client}',
                '{category}',
                '{position}',
                '{rating}'
                )
                ''')

    def display_ratings(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT *
                FROM nieszkolni_app_rating
                ''')

            rows = cursor.fetchall()

            return rows

    def display_unrated_rading(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT c.name, c.assignment_type, c.reference, l.title
                FROM nieszkolni_app_curriculum c
                LEFT JOIN nieszkolni_app_library l
                ON c.reference = l.position_number
                LEFT JOIN nieszkolni_app_rating r
                ON c.reference = r.position
                WHERE NOT EXISTS (
                SELECT NULL
                FROM nieszkolni_app_rating r
                WHERE c.reference = r.position
                )
                AND c.assignment_type = 'reading'
                AND c.name = '{client}'
                AND c.status = 'completed'
                AND c.reference != 0

                ''')

            references = cursor.fetchall()

            print(references)

            return references