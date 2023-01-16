import os
import django
from django.db import connection
from nieszkolni_app.models import Stream
from nieszkolni_app.models import Theater
from nieszkolni_app.models import RepertoireLine
from nieszkolni_app.models import Card
from nieszkolni_app.models import Client
from nieszkolni_app.models import Option
from nieszkolni_app.models import Profile
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re
import pandas as pd

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class StreamManager:
    def __init__(self):
        pass

    def add_to_stream(self, name, command, value, stream_user):
        stamp = TimeMachine().now_number()
        date_number = TimeMachine().today_number()
        date = TimeMachine().today()
        status = "active"

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_stream (
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                )
                VALUES (
                '{stamp}',
                '{date_number}',
                '{date}',
                '{name}',
                '{command}',
                '{value}',
                '{stream_user}',
                '{status}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def import_old_stream(self, stamp, name, date, command, value, email_address):
        stamp = TimeMachine().undefined_date_time_to_number(stamp)
        date_number = TimeMachine().undefined_date_to_number(date)
        value = Cleaner().clean_quotation_marks(value)

        if value is None:
            value = ""
        status = "active"

        if email_address == "dam.zawadzki@gmail.com":
            stream_user = "Damien Bunny"
        elif email_address == "Marta":
            stream_user = "Marta Bubble"
        elif email_address == "asystenttrenerajezykowego@gmail.com":
            stream_user = "Marta Bubble"
        elif email_address == "dam.zawadzki@gmail.com Zawadzki":
            stream_user = "Damien Bunny"
        elif email_address == "coachangielskiego@gmail.com":
            stream_user = "Nadia Cukoo"
        elif email_address == "asystentcoachajezykowego@gmail.com":
            stream_user = "Peter Borough"
        elif email_address == "":
            stream_user = "Damien Bunny"
        elif email_address == "asystentcoachajezykowego@gmail.com ":
            stream_user = "Peter Borough"
        else:
            stream_user = "Damien Bunny"

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_stream (
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                )
                VALUES (
                {stamp},
                {date_number},
                '{date}',
                '{name}',
                '{command}',
                '{value}',
                '{stream_user}',
                '{status}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_stream_range(self, start, end):
        start_date = TimeMachine().date_to_number(start)
        end_date = TimeMachine().date_to_number(end)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status,
                id
                FROM nieszkolni_app_stream
                WHERE date_number >= {start_date}
                AND date_number <= {end_date}
                ''')

            rows = cursor.fetchall()

            return rows

    def display_stream_range_per_client(self, start, end, client):
        start_date = TimeMachine().date_to_number(start)
        end_date = TimeMachine().date_to_number(end)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status,
                id
                FROM nieszkolni_app_stream
                WHERE date_number >= '{start_date}'
                AND date_number <= '{end_date}'
                AND name = '{client}'
                ORDER BY stamp DESC
                ''')

            rows = cursor.fetchall()

            return rows

    def delete_from_stream(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_stream
                WHERE id = {unique_id}
                ''')

    def display_stream_entry(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT stamp, date_number, date, name, command, value, stream_user, status, id
                FROM nieszkolni_app_stream
                WHERE id = {unique_id}
                ''')

            row = cursor.fetchone()

            return row

    def filter_stream_7(self):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE date_number >= ({today_number} - 7)
                AND date_number < {today_number}
                ''')

            rows = cursor.fetchall()

            return rows

    def filter_stream_14(self):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE date_number >= ({today_number} - 14)
                AND date_number < {today_number}
                ''')

            rows = cursor.fetchall()

            return rows

    def filter_stream_28(self):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE date_number >= ({today_number} - 28)
                AND date_number < {today_number}
                ''')

            rows = cursor.fetchall()

            return rows

    def find_by_command(self, command):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE command = '{command}'
                ''')

            rows = cursor.fetchall()

            return rows

    def find_by_command_and_client(self, command, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE command = '{command}'
                AND name = '{client}'
                ''')

            rows = cursor.fetchall()

            return rows

    def add_to_repertoire_line(
            self,
            name,
            title,
            number_of_episodes,
            status
            ):

        now_number = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_repertoireline (
                stamp,
                date,
                name,
                title,
                number_of_episodes,
                status
                )
                VALUES (
                {now_number},
                {today_number},
                '{name}',
                '{title}',
                '{number_of_episodes}',
                '{status}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def check_if_in_repertoire_line(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title
                FROM nieszkolni_app_repertoireline
                WHERE title = '{title}'
                ''')

            title = cursor.fetchone()

            if title is None:
                return False
            else:
                return True

    def activity_points_by_client_week(
            self,
            client,
            description,
            start=None,
            end=None
            ):

        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'Activity'
                AND date_number > '{start_number}'
                AND date_number <= '{end_number}'
                AND value LIKE '{description}%'
                ''')

            rows = cursor.fetchall()

            points = []
            for row in rows:
                try:
                    point_raw = re.search(r";\d+$|;-\d+$", row[0]).group()
                    point = re.sub(";", "", point_raw)
                    point = int(point)

                except Exception as e:
                    point = 0

                points.append(point)

            return points

    def new_cards(self, client, deck, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (english)
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                AND number_of_reviews = 0
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            new_cards = cursor.fetchone()

            return new_cards[0]

    def total_cards(self, client, deck, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (english)
                FROM nieszkolni_app_card
                WHERE client = '{client}'
                AND deck = '{deck}'
                AND number_of_reviews != 0
                AND publication_date > '{start_number}'
                AND publication_date <= '{end_number}'
                ''')

            total_cards = cursor.fetchone()

            return total_cards[0]

    def studied_days(self, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        rows = Card.objects.filter(client=client)

        result = set()
        for row in rows:
            items = row.card_revision_days.split(";")
            for item in items:
                if item != "":
                    item = int(item)
                    if item > start_number and item <= end_number:
                        result.add(item)

        return len(result)

    def studied_days_by_deck(self, client, start, end, deck):
        start = TimeMachine().date_to_number(start)
        end = TimeMachine().date_to_number(end)

        rows = Card.objects.filter(client=client, deck=deck)

        result = set()
        for row in rows:
            items = row.card_revision_days.split(";")
            for item in items:
                if item != "":
                    item = int(item)
                    if item > start and item <= end:
                        result.add(item)

        return len(result)

    def statistics_converter(self, value, unit, decimals):
        if unit == "page":
            result = round(value/250, decimals)
        elif unit == "hour":
            result = round(value/60, decimals)
        elif unit == "hour_minute":
            hours = value // 60
            minutes = value % 60
            result = f"{hours} h {minutes} min"

        return result

    def statistics(self, name):
        client = name
        today_number = TimeMachine().today_number()

        # PV
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'PV'
                ''')

            pv_rows = cursor.fetchall()

            total_PV = 0
            for row in pv_rows:
                try:
                    pv = int(row[5])

                except Exception as e:
                    pv = 0

                total_PV += pv

        # AV
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'AV'
                ''')

            av_rows = cursor.fetchall()

            total_AV = 0
            for row in av_rows:
                av = int(row[5])
                total_AV += av

        # AO
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'AO'
                ''')

            ao_rows = cursor.fetchall()

            total_AO = 0
            for row in ao_rows:
                ao = int(row[5])
                total_AO += ao

        # Duration
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'Duration'
                ''')

            duration_rows = cursor.fetchall()

            total_duration = 0
            for row in duration_rows:
                duration = int(row[5])
                total_duration += duration

        # Repertoire
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration
                FROM nieszkolni_app_theater
                ''')

            repertoire_rows = cursor.fetchall()

            repertoire_dict = dict()
            for row in repertoire_rows:
                title = row[0]
                duration = row[1]
                repertoire_dict.update({title: duration})

        # PO
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'PO'
                ''')

            po_rows = cursor.fetchall()

            po_list = []
            for row in po_rows:
                title = re.sub(r"\s\*\d{1,}", "", row[5])

                try:
                    number_of_episodes = int(re.sub("\s\*","",re.search("\s\*\d{1,}", row[5]).group()))
                except Exception as e:
                    number_of_episodes = 0

                if repertoire_dict.get(title) is None:
                    if self.check_if_in_repertoire_line(title) is False:
                        self.add_to_repertoire_line(client, title, number_of_episodes, "not_in_repertoire")
                        episode_duration = 0
                    else:
                        episode_duration = 0
                else:
                    episode_duration = repertoire_dict.get(title)

                duration = number_of_episodes * episode_duration

                entry = (title, number_of_episodes, episode_duration, duration)
                po_list.append(entry)

            total_po = 0
            for entry in po_list:
                po = entry[3]
                total_po += po

            # Cards
            vocabulary = self.total_cards(name, "vocabulary")
            sentences = self.total_cards(name, "sentences")
            new_vocabulary = self.new_cards(name, "vocabulary")
            new_sentences = self.new_cards(name, "sentences")

            last_sunday = TimeMachine().last_sunday()
            this_sunday = TimeMachine().this_sunday()

            study_days = self.studied_days(name, last_sunday, this_sunday)

            pv_pages = self.statistics_converter(total_PV, "page", 1)
            av_pages = self.statistics_converter(total_AV, "page", 1)
            ao_hours = self.statistics_converter(total_AO, "hour_minute", 1)
            duration_hours = self.statistics_converter(total_duration, "hour_minute", 1)
            po_hours = self.statistics_converter(total_po, "hour_minute", 1)

            stats = {
                "pv": total_PV,
                "av": total_AV,
                "ao": total_AO,
                "duration": total_duration,
                "po": total_po,
                "vocabulary": vocabulary,
                "sentences": sentences,
                "new_vocabulary": new_vocabulary,
                "new_sentences": new_sentences,
                "study_days": study_days,
                "pv_pages": pv_pages,
                "av_pages": av_pages,
                "ao_hours": ao_hours,
                "duration_hours": duration_hours,
                "po_hours": po_hours,
            }

            return stats

    def get_stream_statistics(self, client, command, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = '{command}'
                AND date_number > '{start_number}'
                AND date_number <= '{end_number}'
                ''')

            rows = cursor.fetchall()

            total = 0
            for row in rows:
                try:
                    value = int(row[5])

                except Exception as e:
                    value = 0

                total += value

            return total

    def statistics_range(self, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        total_PV = self.get_stream_statistics(client, "PV", start, end)
        total_AV = self.get_stream_statistics(client, "AV", start, end)
        total_AO = self.get_stream_statistics(client, "AO", start, end)
        total_duration = self.get_stream_statistics(client, "Duration", start, end)
        total_PO = self.count_po_from_to(client, start, end)
        vocabulary = self.total_cards(client, "vocabulary")
        sentences = self.total_cards(client, "sentences")
        new_vocabulary = self.new_cards(client, "vocabulary")
        new_sentences = self.new_cards(client, "sentences")

        study_days = self.studied_days(client, start, end)

        stats = {
            "pv": total_PV,
            "av": total_AV,
            "ao": total_AO,
            "duration": total_duration,
            "po": total_PO,
            "vocabulary": vocabulary,
            "sentences": sentences,
            "new_vocabulary": new_vocabulary,
            "new_sentences": new_sentences,
            "study_days": study_days
            }

        return stats

    def count_po(self, client, title_type, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        # Repertoire
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration
                FROM nieszkolni_app_theater
                WHERE title_type = '{title_type}'
                ''')

            repertoire_rows = cursor.fetchall()

            repertoire_dict = dict()
            for row in repertoire_rows:
                title = row[0]
                duration = row[1]
                repertoire_dict.update({title: duration})

        # PO
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'PO'
                AND date_number > '{start_number}'
                AND date_number <= '{end_number}'
                ''')

            po_rows = cursor.fetchall()

            po_list = []
            for row in po_rows:
                title = re.sub(r"\s\*\d{1,}", "", row[5])

                try:
                    number_of_episodes = int(re.sub("\s\*","",re.search("\s\*\d{1,}", row[5]).group()))
                except Exception as e:
                    number_of_episodes = 0

                if repertoire_dict.get(title) is None:
                    episode_duration = 0
                else:
                    episode_duration = repertoire_dict.get(title)

                duration = number_of_episodes * episode_duration

                entry = (title, number_of_episodes, episode_duration, duration)
                po_list.append(entry)

            total_po = 0
            for entry in po_list:
                po = entry[3]
                total_po += po

            return total_po

    def count_po_from_to(self, client, start=None, end=None):
        start_number = TimeMachine().get_start_end_number(start, end)["start"]
        end_number = TimeMachine().get_start_end_number(start, end)["end"]

        # Repertoire
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration
                FROM nieszkolni_app_theater
                ''')

            repertoire_rows = cursor.fetchall()

            repertoire_dict = dict()
            for row in repertoire_rows:
                title = row[0]
                duration = row[1]
                repertoire_dict.update({title: duration})

        # PO
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                date,
                name,
                command,
                value,
                stream_user,
                status
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'PO'
                AND date_number > '{start_number}'
                AND date_number <= '{end_number}'
                ''')

            po_rows = cursor.fetchall()

            po_list = []
            for row in po_rows:
                title = re.sub(r"\s\*\d{1,}", "", row[5])

                try:
                    number_of_episodes = int(re.sub("\s\*","",re.search("\s\*\d{1,}", row[5]).group()))
                except Exception as e:
                    number_of_episodes = 0

                if repertoire_dict.get(title) is None:
                    episode_duration = 0
                else:
                    episode_duration = repertoire_dict.get(title)

                duration = number_of_episodes * episode_duration

                entry = (title, number_of_episodes, episode_duration, duration)
                po_list.append(entry)

            total_po = 0
            for entry in po_list:
                po = entry[3]
                total_po += po

            return total_po

    def find_command_from_to(self, client, command, start, end):
        dates = TimeMachine().list_dates(start, end)

        rows = Stream.objects.filter(
                name=client,
                command=command,
                date__in=dates
                )

        return rows

    def display_titles_per_client(self, client):

        # Theater
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                id
                FROM nieszkolni_app_theater
                ''')

            repertoire_rows = cursor.fetchall()

            repertoire_dict = dict()
            for row in repertoire_rows:
                title = row[0]
                unique_id = row[1]
                repertoire_dict.update({title: unique_id})

        # PO
        start = TimeMachine().date_to_number("2022-12-01")

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT value
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'PO'
                AND date_number >= '{start}'
                ''')

            po_rows = cursor.fetchall()

            titles = set()
            for row in po_rows:
                title = re.sub(r"\s\*\d{1,}", "", row[0])

                if repertoire_dict.get(title) is not None:
                    unique_id = repertoire_dict.get(title)
                    titles.add(unique_id)

            return titles

    def advanced_statistics(self, name):
        client = name
        today_number = TimeMachine().today_number()

        # Series and movies
        series = self.count_po(client, "tv_series")
        movies = self.count_po(client, "movie")

        series_and_movies = series + movies

        # Podcasts and audiobooks
        podcasts = self.count_po(client, "podcast")
        audiobooks = self.count_po(client, "audiobook")

        podcasts_and_audiobooks = podcasts + audiobooks

        stats = {
            "series_and_movies": series_and_movies,
            "podcasts_and_audiobooks": podcasts_and_audiobooks,
            }

        return stats

    def display_activity_start(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_option
                WHERE command = 'activity_start'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                activity_start = "2022-01-01"
            else:
                activity_start = data[0]

            return activity_start

    def display_activity_stop(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_option
                WHERE command = 'activity_stop'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                activity_stop = "2022-01-01"
            else:
                activity_stop = data[0]

            return activity_stop

    def display_activity(self, client):
        activity_start = TimeMachine().date_to_number(self.display_activity_start())
        activity_stop = TimeMachine().date_to_number(self.display_activity_stop())

        # Activity
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE date_number >= {activity_start}
                AND date_number <= {activity_stop}
                AND name = '{client}'
                AND command = 'Activity'
                ''')

            rows = cursor.fetchall()

            activity = []
            activity_history = []
            for row in rows:
                entry = row[0]

                try:
                    point_raw = re.search(r";\d+$|;-\d+$", entry).group()
                    point = re.sub(";", "", point_raw)
                    point = int(point)
                    activity.append(point)

                    description_raw = re.search(r"\w.+;", entry).group()
                    description = re.sub(";", "", description_raw)
                    history = (description, point)
                    activity_history.append(history)

                except Exception as e:
                    pass

            activity_points = sum(activity)

            return activity_points

    def display_activity_target(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                value
                FROM nieszkolni_app_stream
                WHERE name = '{client}'
                AND command = 'Activity target'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                target = 99
            else:
                target = int(data[0])

            return target

    def display_display_names(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                display_name,
                avatar
                FROM nieszkolni_app_profile
                ''')

            rows = cursor.fetchall()

            names = dict()
            for row in rows:
                names.update({row[0]: (row[1], row[2])})

            return names

    def display_ranking(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                display_name
                FROM nieszkolni_app_profile
                ''')

            names = cursor.fetchall()

        activity_start = TimeMachine().date_to_number(self.display_activity_start())
        activity_stop = TimeMachine().date_to_number(self.display_activity_stop())

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                value,
                name
                FROM nieszkolni_app_stream
                WHERE date_number >= {activity_start}
                AND date_number <= {activity_stop}
                AND command = 'Activity'
                ''')

            rows = cursor.fetchall()

            activity = []
            clients = []
            data = ({"client": clients, "activity": activity})
            for row in rows:
                line = row[0]

                try:
                    point_raw = re.search(r";\d+$|;-\d+$", line).group()
                    point = re.sub(";", "", point_raw)
                    point = int(point)
                    activity.append(point)

                    client = row[1]
                    clients.append(client)

                except Exception as e:
                    pass

            table = pd.DataFrame(data, columns=["client", "activity"])
            table_2 = table.groupby("client").sum()
            table_3 = table_2.sort_values(by="activity", ascending=False)
            table_4 = table_3.reset_index()
            table_4.index = table_4.index + 1
            table_4["rank"] = table_4["activity"].rank(
                    method="dense",
                    na_option="bottom",
                    ascending=False
                    ).astype(int)
            table_5 = list(table_4.itertuples(index=True, name=None))
            entries = table_5

            profiles = self.display_display_names()
            ranking = []
            for entry in entries:

                position = entry[3]
                client = entry[1]
                activity_points = entry[2]

                if profiles.get(entry[1]) is None:
                    display_name = entry[1]
                    avatar = ""
                else:
                    display_name = profiles.get(entry[1])[0]
                    avatar = profiles.get(entry[1])[1]

                item = (position, display_name, activity_points, client, avatar)

                ranking.append(item)

            return ranking

    def display_ranking_by_client(self, client):
        rows = self.display_ranking()

        for row in rows:
            if row[3] == client:
                position = row[0]
                return position

        return 0

    # Spins and stories

    def display_planned_stories(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE command = 'Planned story'
                AND name = '{client}'
                ''')

            rows = cursor.fetchall()
            stories = [int(row[0]) for row in rows]

            return stories

    def display_stories(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE command = 'Covered story'
                AND name = '{client}'
                ''')

            rows = cursor.fetchall()
            covered_stories = [int(row[0]) for row in rows]
            planned_stories = self.display_planned_stories(client)

            stories = planned_stories.copy()
            for story in covered_stories:
                if story in stories:
                    stories.remove(story)

            return stories

    def display_planned_challenges(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE command = 'Planned challenge'
                AND name = '{client}'
                ''')

            rows = cursor.fetchall()
            challenges = [row[0] for row in rows]

            return challenges

    def display_challenges(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_stream
                WHERE command = 'Covered challenge'
                AND name = '{client}'
                ''')

            rows = cursor.fetchall()
            covered_challenges = [row[0] for row in rows]
            planned_challenges = self.display_planned_challenges(client)

            challenges = planned_challenges.copy()
            for challenge in covered_challenges:
                if challenge in challenges:
                    challenges.remove(challenge)

            return challenges