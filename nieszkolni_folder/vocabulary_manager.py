import os
import django

from django.db import connection

from nieszkolni_app.models import Card
from nieszkolni_app.models import Client

from nieszkolni_folder.time_machine import TimeMachine

import json

import pandas as pd


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class VocabularyManager:
    def __init__(self):
        pass

    # User specific functions
    def add_entry(
            self,
            client,
            deck,
            english,
            polish,
            coach,
            initiation_date=None
            ):

        entry = Card()
        today = TimeMachine().today()
        today_number = TimeMachine().date_to_number(today)

        if initiation_date is None:
            initiation_date = today_number

        unique_id_list = Card.objects.values_list("card_id", flat=True)
        if len(unique_id_list) == 0:
            entry.card_id = 1
        else:
            last_card_id = max(list(unique_id_list))
            entry.card_id = last_card_id + 1

        vocabulary = Card.objects.filter(client__contains=client).values("english")
        vocabulary = [item.get("english") for item in list(vocabulary)]
        if english in vocabulary:
            pass
        else:
            entry.client = client
            entry.deck = deck
            entry.english = english
            entry.polish = polish
            entry.publication_date = today_number
            entry.due_date = today_number
            entry.interval = 0
            entry.number_of_reviews = 0
            entry.answers = ""
            entry.card_opening_times = ""
            entry.card_closing_times = ""
            entry.card_revision_days = ""
            entry.line = 1
            entry.coach = coach
            entry.initiation_date = initiation_date
            entry.save()

    def display_all_entries(self, client, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                ''')

            entries = cursor.fetchall()

            return entries

    def display_all_cards(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                ''')

            entries = cursor.fetchall()

            return entries

    def display_cards(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                ''')

            entries = cursor.fetchall()

            return entries

    def display_card(self, card_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                WHERE card_id = '{card_id}'
                ''')

            entry = cursor.fetchone()

            return entry

    def display_due_entries(self, client, deck):
        old_entries = self.display_old_due_entries(client, deck)
        new_entries = self.display_new_due_entries(client, deck)
        problematic_entries = self.display_problematic_due_entries(client, deck)

        entries_raw = problematic_entries + old_entries + new_entries
        entries = sorted(entries_raw, key=lambda tup: tup[4], reverse=False)

        return entries

    def display_counts(self, client, deck):
        old = len(self.display_old_due_entries(client, deck))
        new = len(self.display_new_due_entries(client, deck))
        problematic = len(self.display_problematic_due_entries(client, deck))

        counts = [old, new, problematic]

        return counts

    def display_due_entries_json(self, client, deck):
        check = Card.objects.filter(client=client).exists()

        if not check:
            return None

        entries = self.display_due_entries(client, deck)
        counts = self.display_counts(client, deck)
        total = sum(counts)

        if len(entries) != 0:
            things = list(entries[0])
            things.extend(counts)
            things.append(total)

            result = [str(thing) for thing in things]
            result = "<>".join(result)

            return result

        else:
            return None

    def display_old_due_entries(self, client, deck):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                polish,
                english,
                interval,
                line
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                AND due_date <= {today_number}
                AND number_of_reviews != 0
                AND interval != 0
                AND english != ''
                ''')

            entries = cursor.fetchall()

            return entries

    def display_new_entries_done_today(self, client, deck):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (DISTINCT card_id)
                FROM nieszkolni_app_card
                WHERE card_revision_days LIKE ';{today_number}%'
                AND client = '{client}'
                AND deck = '{deck}'
                AND number_of_reviews > 0
                ''')

            data = cursor.fetchone()
            result = data[0]

            return result

    def display_new_due_entries(self, client, deck):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                polish,
                english,
                interval,
                line
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                AND due_date <= {today_number}
                AND number_of_reviews = 0
                AND english != ''
                ''')

            entries = cursor.fetchall()

            info = Client.objects.get(name=client)

            if deck == "vocabulary":
                daily_limit_of_new_cards = info.daily_limit_of_new_vocabulary
            elif deck == "sentences":
                daily_limit_of_new_cards = info.daily_limit_of_new_sentences

            new_cards_done_today = self.display_new_entries_done_today(client, deck)
            actual_daily_limit_of_new_cards = daily_limit_of_new_cards - new_cards_done_today

            if actual_daily_limit_of_new_cards > 0:
                return entries[0:actual_daily_limit_of_new_cards]
            else:
                return []

    def display_problematic_due_entries(self, client, deck):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                polish,
                english,
                interval,
                line
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                AND due_date <= {today_number}
                AND number_of_reviews != 0
                AND interval = 0
                AND english != ''
                ORDER BY line ASC 
                ''')

            entries = cursor.fetchall()

            return entries

    def update_card(self, card_id, answer, card_opening_time):
        entry = Card.objects.get(card_id=card_id)

        today = TimeMachine().today()
        today_number = TimeMachine().date_to_number(today)

        now = TimeMachine().now_colons()
        now_number = TimeMachine().date_time_to_number(now)

        deck = entry.deck
        client = entry.client
        info = Client.objects.get(name=client)

        if deck == "vocabulary":
            maximal_interval = info.maximal_interval_vocabulary
        elif deck == "sentences":
            maximal_interval = info.maximal_interval_sentences

        if answer == "incorrect":
            rate = 0.0

        elif answer == "hard":
            rate = 1.0

        elif answer == "easy":
            rate = 1.5

        else:
            pass

        if entry.line == None:
            line = 1
        else:
            line = entry.line + 1

        entry.line = line
        interval = round((entry.interval + 1) * rate)

        if maximal_interval < interval:
            entry.interval = maximal_interval
        else:
            entry.interval = interval

        entry.due_date = today_number + interval
        entry.number_of_reviews = entry.number_of_reviews + 1

        answers = entry.answers
        if answers is None:
            entry.answers = answer
        else:
            entry.answers = answers + ";" + answer

        card_opening_times = entry.card_opening_times
        if card_opening_times is None:
            entry.card_opening_times = str(card_opening_time)
        else:
            entry.card_opening_times = str(card_opening_times) + ";" + str(card_opening_time)

        card_closing_times = entry.card_closing_times
        if card_closing_times is None:
            entry.card_closing_times = str(now_number)
        else:
            entry.card_closing_times = str(card_closing_times) + ";" + str(now_number)

        durations = entry.durations
        if durations is None:
            entry.durations = str(now_number - card_opening_time)
        else:
            entry.durations = durations + ";" + str(now_number - card_opening_time)

        card_revision_days = entry.card_revision_days
        if card_revision_days is None:
            entry.card_revision_days = str(today_number)
        else:
            entry.card_revision_days = str(card_revision_days) + ";" + str(today_number) 

        entry.save()

    def reset_line(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE nieszkolni_app_card SET line = 0 WHERE client = '{client}'")

        return "done"

    def total_cards(self, client):
        total_cards = Card.objects.raw(f"SELECT DISTINCT card_id FROM nieszkolni_app_card WHERE client = '{client}'")
        total_cards = len(total_cards)

        return total_cards

    def new_cards(self, client, deck):
        new_cards = Card.objects.raw(f"SELECT DISTINCT card_id FROM nieszkolni_app_card WHERE client = '{client}' AND number_of_reviews = 0 AND deck = '{deck}'")
        new_cards = len(new_cards)

        return new_cards

    def edit_cards(
            self,
            card_id,
            english,
            polish
            ):

        pattern = Card.objects.get(pk=card_id)

        cards = Card.objects.filter(
                polish=pattern.polish,
                english=pattern.english
                )

        for card in cards:
            card.polish = polish
            card.english = english
            card.save()

    def edit_card(self, card_id, polish, english):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_card
                SET polish = '{polish}',
                english = '{english}'
                WHERE card_id = {card_id}
                ''')

        return "Card edited!"

    def delete_card(self, card_id):
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM nieszkolni_app_card WHERE card_id = {card_id}")

        return "Card deleted!"

    def remove_cards(
            self,
            card_id
            ):

        pattern = Card.objects.get(pk=card_id)

        cards = Card.objects.filter(
                polish=pattern.polish,
                english=pattern.english
                ).delete()

    # Deck specific functions
    def download_database(self):
        database = []

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM nieszkolni_app_card")
            rows = cursor.fetchall()

        for row in rows:
            database.append(row)

        return database

    def display_test_cards(self, client, deck):
        if deck == "vocabulary":
            limit = 20
        else:
            limit = 10

        today_number = TimeMachine().today_number()
        deadline = today_number - 14

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                deck,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND number_of_reviews != 0
                AND publication_date <= '{deadline}'
                AND deck = '{deck}'
                ORDER BY RANDOM() LIMIT {limit}
                ''')

            cards = cursor.fetchall()

        return cards

    def remove_all_new_cards(self, client):
        Card.objects.filter(client=client, number_of_reviews=0).delete()

    def remove_card(self, card_id):
        card = Card.objects.filter(card_id=card_id)

        if card.exists():
            card.delete()

    def display_cards_time(self, client, deck):
        today_number = TimeMachine().today_number()
        deadline = today_number - 2

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                durations,
                card_revision_days
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND number_of_reviews != 0
                AND deck = '{deck}'
                AND durations != ''
                AND card_revision_days != ''
                ''')

            cards = cursor.fetchall()

            entries = []
            for card in cards:
                durations = card[0][1:].split(";")
                days = card[1][1:].split(";")

                entry = map(
                        lambda x, y:
                        (x, y),
                        durations,
                        days
                        )

                entries.extend(list(entry))

            return entries

    def count_study_time_per_day(self, client, deck):
        entries = self.display_cards_time(client, deck)

        days = set([entry[1] for entry in entries])
        data = []

        for day in days:
            rows = [
                int(entry[0]) if int(entry[0]) <= 60 else 60
                for entry in entries
                if entry[1] == day
                ]

            duration = round(sum(rows)/60, 1)

            day_text = TimeMachine().number_to_system_date(day)

            data.append((day, day_text, duration))

        data.sort(key=lambda x: x[0], reverse=True)

        return data

    def display_cards_studied_per_date(self, client, date):
        date_number = TimeMachine().date_to_number(date)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                card_id,
                english,
                polish,
                interval
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND card_revision_days LIKE ';{date_number}%'
                ''')

            entries = cursor.fetchall()

            return entries