import os
import django
from django.db import connection
from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.back_office_manager import BackOfficeManager

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

    def display_unrated_reading(self, client):
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
                WHERE r.position = c.reference
                AND r.client = '{client}'
                )
                AND c.assignment_type = 'reading'
                AND c.name = '{client}'
                AND c.status = 'completed'
                AND c.reference != 0

                ''')

            unrated = cursor.fetchall()

            return unrated

    def display_unrated_listening(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT position
                FROM nieszkolni_app_rating
                WHERE client = '{client}'
                AND category = 'listening'
                ''')

            references = cursor.fetchall()

        references = set(reference[0] for reference in references)
        titles = StreamManager().display_titles_per_client(client)
        titles.difference_update(references)

        unrated = [(
            client,
            "listening",
            title,
            BackOfficeManager().find_position_in_theater(title)[0]
            )
            for title
            in titles
            ]

        return unrated

    def display_unrated(self, client):
        reading = self.display_unrated_reading(client)
        listening = self.display_unrated_listening(client)

        unrated = []
        unrated.extend(reading)
        unrated.extend(listening)

        return unrated

    def display_ratings(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                position,
                category,
                rating
                FROM nieszkolni_app_rating
                ''')

            rows = cursor.fetchall()

        entries = []

        if rows is not None:
            for row in rows:

                if row[1] == "reading" or row[1] == "listening":
                    if row[1] == "reading":
                        title = BackOfficeManager().find_position_in_library(row[0])[1]
                    elif row[1] == "listening":
                        title = BackOfficeManager().find_position_in_theater(row[0])[0]

                    entry = (
                        row[0],
                        row[1],
                        row[2],
                        title
                        )

                    entries.append(entry)

        positions = {entry[0] for entry in entries}

        ratings = []
        for position in positions:
            category = list({entry[1] for entry in entries if entry[0] == position})
            category = category[0]
            title = list({entry[3] for entry in entries if entry[0] == position})
            title = title[0]

            votes = [entry[2] for entry in entries if entry[0] == position]
            total = len(votes)
            postive = votes.count(1)
            result = round(postive/total * 100)

            rating = (
                category,
                title,
                total,
                result
                )

            ratings.append(rating)

        ratings.sort(key=lambda item: (item[0], item[3]))

        return ratings

