import os
import django

from django.db import connection

from nieszkolni_app.models import Client

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class AnalyticsManager:
    def __init__(self):
        pass

    def new_cards(self, coach, client, deck, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (english)
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND coach = '{coach}'
                AND deck = '{deck}'
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            card_data = cursor.fetchone()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (english)
                FROM nieszkolni_app_book
                WHERE name = '{client}'
                AND publicating_user = '{coach}'
                AND deck = '{deck}'
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            book_data = cursor.fetchone()

        result = int(card_data[0]) + int(book_data[0])
        return result

    def new_pronunciation(self, coach, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (entry)
                FROM nieszkolni_app_pronunciation
                WHERE name = '{client}'
                AND coach = '{coach}'
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            data = cursor.fetchone()

        result = int(data[0])
        return result

    def new_memories(self, coach, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (prompt)
                FROM nieszkolni_app_memory
                WHERE name = '{client}'
                AND coach = '{coach}'
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            data = cursor.fetchone()

        result = int(data[0])
        return result

    def count_new_entries_for_student(
            self,
            coach,
            client,
            start=None,
            end=None
            ):

        new_vocabulary = self.new_cards(coach, client, "vocabulary", start, end)
        new_sentences = self.new_cards(coach, client, "sentences", start, end)
        new_pronunciation = self.new_pronunciation(coach, client, start, end)
        new_memories = self.new_memories(coach, client, start, end)
        total_new_entries = new_vocabulary + new_sentences + new_pronunciation + new_memories

        statistics = {
            "coach": coach,
            "client": client,
            "new_vocabulary": new_vocabulary,
            "new_sentences": new_sentences,
            "new_pronunciation": new_pronunciation,
            "new_memories": new_memories,
            "total_new_entries": total_new_entries
            }

        return statistics

    def count_new_entries_per_student(self, coach, start=None, end=None):
        clients = Client.objects.filter(coach=coach)

        entries = []
        for client in clients:
            entry = self.count_new_entries_for_student(
                    coach,
                    client.name,
                    start,
                    end
                    )
            entries.append(entry)

        entries.sort(key=lambda entry: entry["total_new_entries"], reverse=True)

        return entries

    def count_new_entries_per_student_last_week(self, coach):
        last_sunday = TimeMachine().last_sunday()
        previous_sunday = TimeMachine().previous_sunday(last_sunday)

        data = self.count_new_entries_per_student(
                coach,
                previous_sunday,
                last_sunday
                )

        return data

    def count_all_new_entries_per_student_last_week(self):
        coaches = Client.objects.filter(user_type="coach", status="active")
        data = []
        for coach in coaches:
            entries = self.count_new_entries_per_student_last_week(coach.name)
            data.extend(entries)

        data.sort(key=lambda entry: entry["total_new_entries"], reverse=True)

        return data
