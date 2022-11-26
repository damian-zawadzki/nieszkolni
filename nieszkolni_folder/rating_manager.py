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
            position,
            rating
            ):

        date_number = TimeMachine().today_number()
        position = Cleaner().clean_quotation_marks(position)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_rating (
                date_number,
                client,
                position,
                rating
                )
                VALUES (
                '{date_number}',
                '{client}',
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