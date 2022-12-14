import os
import django
from django.db import connection
from nieszkolni_app.models import Card
from nieszkolni_folder.time_machine import TimeMachine


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class VocabularyManager:
    def __init__(self):
        pass

    # User specific functions
    def add_entry(self, client, deck, english, polish, coach):
        entry = Card()
        today = TimeMachine().today()
        today_number = TimeMachine().date_to_number(today)

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

    def display_due_entries(self, client, deck):
        old_entries = self.display_old_due_entries(client, deck)
        new_entries = self.display_new_due_entries(client, deck)
        problematic_entries = self.display_problematic_due_entries(client, deck)

        entries_raw = problematic_entries + old_entries + new_entries
        entries = sorted(entries_raw, key=lambda tup: tup[4], reverse=False)

        return entries

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
                ''')

            entries = cursor.fetchall()

            daily_limit_of_new_cards = self.current_daily_limit_of_new_cards(client)
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

    def current_daily_limit_of_new_cards(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT daily_limit_of_new_cards FROM nieszkolni_app_client WHERE name = '{client}'")
            current_daily_limit_of_new_cards = cursor.fetchone()

        if current_daily_limit_of_new_cards is None:
            current_daily_limit_of_new_cards = 25
        else:
            current_daily_limit_of_new_cards = current_daily_limit_of_new_cards[0]

        return current_daily_limit_of_new_cards

    def update_current_daily_limit_of_new_cards(self, client, limit):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT daily_limit_of_new_cards FROM nieszkolni_app_client WHERE name = '{client}'")
            current_daily_limit_of_new_cards = cursor.fetchone()

            if current_daily_limit_of_new_cards is None:
                cursor.execute(f"INSERT INTO nieszkolni_app_client (daily_limit_of_new_cards, name) VALUES({limit}, '{client}')")
            else:
                cursor.execute(f"UPDATE nieszkolni_app_client SET daily_limit_of_new_cards = {limit} WHERE name = '{client}'")

        return "done"

    def edit_card(self, card_id, polish, english):
        with connection.cursor() as cursor:
           cursor.execute(f"UPDATE nieszkolni_app_card SET polish = '{polish}', english = '{english}' WHERE card_id = {card_id}")

        return "Card edited!"

    def delete_card(self, card_id):
        with connection.cursor() as cursor:
           cursor.execute(f"DELETE FROM nieszkolni_app_card WHERE card_id = {card_id}")

        return "Card deleted!"

    # Deck specific functions
    def download_database(self):
        database = []

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM nieszkolni_app_card")
            rows = cursor.fetchall()

        for row in rows:
            database.append(row)

        return database