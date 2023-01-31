import os
import django

from django.db import connection

from nieszkolni_app.models import Client
from nieszkolni_app.models import Stream
from nieszkolni_app.models import Card
from nieszkolni_app.models import Memory
from nieszkolni_app.models import Pronunciation
from nieszkolni_app.models import Grade

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

from nieszkolni_folder.stream_manager import StreamManager

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

        entries.sort(key=lambda entry: entry["total_new_entries"])

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

        data.sort(key=lambda entry: entry["total_new_entries"])

        return data

    def get_seniority(self, client):
        today = TimeMachine().today()

        lessons = Stream.objects.filter(name=client, command="Duration")
        if not lessons.exists():
            return 1

        first_lesson = lessons.order_by("date_number")[0]

        seniority = TimeMachine().count_seniority(first_lesson.date, today)

        return seniority

    def count_entry_rate_for_student(self, client):
        seniority = self.get_seniority(client)

        vocabulary = Card.objects.filter(client=client, deck="vocabulary")
        sentences = Card.objects.filter(client=client, deck="sentences")
        memories = Memory.objects.filter(name=client)
        pronunciation = Pronunciation.objects.filter(name=client)

        rates = {}

        rates.update({"vocabulary_rate": round(len(vocabulary) / seniority)})
        rates.update({"sentences_rate": round(len(sentences) / seniority)})
        rates.update({"memories_rate": round(len(memories) / seniority)})
        rates.update({"pronunciation_rate": round(len(pronunciation) / seniority)})

        average_rate = round(sum(rates.values())/len(rates.values()), 1)
        rates.update({"average_rate": average_rate})
        rates.update({"client": client})

        return rates

    def count_entry_rate_per_student(self, coach):
        clients = Client.objects.filter(coach=coach)

        entries = []
        for client in clients:
            entry = self.count_entry_rate_for_student(
                    client.name
                    )
            entry.update({"coach": coach})
            entries.append(entry)

        entries.sort(key=lambda entry: entry["average_rate"])

        return entries

    def count_all_entry_rate_per_student(self):
        coaches = Client.objects.filter(user_type="coach", status="active")
        data = []
        for coach in coaches:
            entries = self.count_entry_rate_per_student(coach.name)
            data.extend(entries)

        data.sort(key=lambda entry: entry["average_rate"])

        return data

    def count_entry_total_for_student(self, client):
        vocabulary = Card.objects.filter(client=client, deck="vocabulary")
        sentences = Card.objects.filter(client=client, deck="sentences")
        memories = Memory.objects.filter(name=client)
        pronunciation = Pronunciation.objects.filter(name=client)

        totals = {}

        totals.update({"vocabulary": len(vocabulary)})
        totals.update({"sentences": len(sentences)})
        totals.update({"memories": len(memories)})
        totals.update({"pronunciation": len(pronunciation)})

        total = sum(totals.values())
        totals.update({"total": total})
        totals.update({"client": client})

        return totals

    def count_entry_total_per_student(self, coach):
        clients = Client.objects.filter(coach=coach)

        entries = []
        for client in clients:
            entry = self.count_entry_total_for_student(
                    client.name
                    )
            entry.update({"coach": coach})
            entries.append(entry)

        entries.sort(key=lambda entry: entry["total"])

        return entries

    def count_all_entry_total_per_student(self):
        coaches = Client.objects.filter(user_type="coach", status="active")
        data = []
        for coach in coaches:
            entries = self.count_entry_total_per_student(coach.name)
            entries[0].update({"coach": coach.name})
            data.extend(entries)

        data.sort(key=lambda entry: entry["total"])

        return data

    def get_grade_range(self, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        clients = Client.objects.filter(
                status="active",
                user_type="client"
                ).values_list(
                "name", flat=True
                )

        grades = []
        for client in clients:
            count = Grade.objects.filter(
                date_number__gte=start_number,
                date_number__lte=end_number,
                student=client
                ).count()

            grades.append((client, count))

        grades.sort(key=lambda x: x[1])
        return grades

    def current_average_score_per_coach(self):
        coaches = Client.objects.filter(
                status="active",
                user_type="coach"
                ).values_list(
                "name", flat=True
                )

        results = []
        for coach in coaches:
            result = self.current_average_score_for_coach(coach)
            results.append(result)

        return results

    def current_average_score_for_coach(self, coach):
        clients = Client.objects.filter(
                status="active",
                user_type="client",
                coach=coach
                ).values_list(
                "name", flat=True
                )

        total = []

        for client in clients:
            points = StreamManager().display_activity(client)
            total.append(points)

        average = round(sum(total)/len(clients), 1)

        return (coach, average)
