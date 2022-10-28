import os
import django
from django.db import connection
from nieszkolni_app.models import Stream
from nieszkolni_app.models import Repertoire
from nieszkolni_app.models import RepertoireLine
from nieszkolni_app.models import Card
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

    def import_old_stream(self, stamp, name, date, command, value, email_address):
        stamp = TimeMachine().date_time_to_number(stamp)
        date_number = TimeMachine().date_to_number(date)
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

    def delete_from_stream(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_stream
                WHERE id = {unique_id}
                ''')

    def display_stream_entry(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT stamp, date_number, date, name, command, value, stream_user, status
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

    def total_cards(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT (english)
                FROM nieszkolni_app_card
                WHERE deck = '{deck}'
                ''')

            total_cards = cursor.fetchone()

            return total_cards[0]

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

                except:
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
                FROM nieszkolni_app_repertoire
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
                print(row[5])

                try:
                    number_of_episodes = int(re.sub("\s\*","",re.search("\s\*\d{1,}", row[5]).group()))
                except:
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

            # Total cards
            vocabulary = self.total_cards("vocabulary")
            sentences = self.total_cards("sentences")

            stats = {
                "pv": total_PV,
                "av": total_AV,
                "ao": total_AO,
                "duration": total_duration,
                "po": total_po,
                "vocabulary": vocabulary,
                "sentences": sentences
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
                SELECT
                value
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
                    point_raw = re.search(r";\d+$", entry).group()
                    point = re.sub(";", "", point_raw)
                    point = int(point)
                    activity.append(point)

                    description_raw = re.search(r"\w.+;", entry).group()
                    description = re.sub(";", "", description_raw)
                    history = (description, point)
                    activity_history.append(history)

                except:
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
                display_name
                FROM nieszkolni_app_profile
                ''')

            rows = cursor.fetchall()

            names = dict()
            for row in rows:
                names.update({row[0]: row[1]})

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
                    point_raw = re.search(r";\d+$", line).group()
                    point = re.sub(";", "", point_raw)
                    point = int(point)
                    activity.append(point)

                    client = row[1]
                    clients.append(client)

                except:
                    pass

            table = pd.DataFrame(data, columns=["client", "activity"])
            table_2 = table.groupby("client").sum()
            table_3 = table_2.sort_values(by="activity", ascending=False)
            table_4 = table_3.reset_index()
            table_4.index = table_4.index + 1
            table_5 = list(table_4.itertuples(index=True, name=None))
            entries = table_5

            display_names = self.display_display_names()
            ranking = []
            for entry in entries:

                if display_names.get(entry[1]) is None:
                    display_name = entry[1]
                else:
                    display_name = display_names.get(entry[1])

                item = (entry[0], display_name, entry[2])

                ranking.append(item)

            return ranking