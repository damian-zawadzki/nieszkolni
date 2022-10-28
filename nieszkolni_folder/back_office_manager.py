import os
import django
from django.db import connection
from nieszkolni_app.models import Library
from nieszkolni_app.models import LibraryLine
from nieszkolni_app.models import Repertoire
from nieszkolni_app.models import RepertoireLine
from nieszkolni_app.models import Notification
from nieszkolni_app.models import Option
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class BackOfficeManager:
    def __init__(self):
        today_pattern = "%Y-%m-%d"

    def add_to_library(
            self,
            position_number,
            title,
            wordcount,
            link
            ):

        title = Cleaner().clean_quotation_marks(title)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_library (
                position_number,
                title,
                wordcount,
                link
                )
                VALUES (
                {position_number},
                '{title}',
                {wordcount},
                '{link}'
                )
                ON CONFLICT (position_number)
                DO NOTHING
                ''')

    def delete_from_library(self, position_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_library
                WHERE position_number = {position_number}
                ''')

    def display_library(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                position_number,
                title,
                wordcount,
                link
                FROM nieszkolni_app_library
                ''')

            positions = cursor.fetchall()

            return positions

    def display_library_position_numbers(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                position_number
                FROM nieszkolni_app_library
                ''')

            entries = cursor.fetchall()
            positions = [entry[0] for entry in entries]

            return positions

    def find_position_in_library(self, position_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                position_number,
                title,
                wordcount,
                link
                FROM nieszkolni_app_library
                WHERE position_number = {position_number}
                ''')

            position = cursor.fetchone()

            return position

    def check_if_in_library(self, link):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                position_number
                FROM nieszkolni_app_library
                WHERE link = '{link}'
                ''')

            position_number = cursor.fetchone()

            if position_number is None:
                return False
            else:
                return True

    def get_wordcount_from_library(self, link):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                wordcount
                FROM nieszkolni_app_library
                WHERE link = '{link}'
                ''')

            wordcount = cursor.fetchone()

            if wordcount is None:
                return None
            else:
                return wordcount[0]

    def add_to_library_line(
            self,
            name,
            link,
            status
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_libraryline (
                name,
                link,
                status
                )
                VALUES (
                '{name}',
                '{link}',
                '{status}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_reported_library_line(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                link
                FROM nieszkolni_app_libraryline
                WHERE status = 'reported'
                ''')

            links = cursor.fetchall()

            if len(links) == 0:
                return None
            else:
                link = links[0]
                return link

    def next_custom_postion_number(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT MAX(position_number)
                FROM nieszkolni_app_library
                WHERE position_number > 9999
                ''')

            last_custom_postion_number = cursor.fetchone()

            if last_custom_postion_number[0] is None:
                next_custom_postion_number = 10000
                return next_custom_postion_number

            else:
                next_custom_postion_number = last_custom_postion_number[0] + 1

                return next_custom_postion_number

    def mark_library_line_as_processed(self, name, link):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_libraryline
                SET status = 'processed'
                WHERE name = '{name}'
                AND link = '{link}'
                ''')

    def add_to_repertoire(
            self,
            title,
            duration,
            title_type
            ):

        title = Cleaner().clean_quotation_marks(title)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_repertoire (
                title,
                duration,
                title_type
                )
                VALUES (
                '{title}',
                {duration},
                '{title_type}'
                )
                ON CONFLICT (title)
                DO NOTHING
                ''')

    def delete_from_repertoire(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_repertoire
                WHERE title = '{title}'
                ''')

    def display_repertoire(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration,
                title_type
                FROM nieszkolni_app_repertoire
                ''')

            titles = cursor.fetchall()

            return titles

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

    def display_reported_repertoire_line(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date,
                name,
                title,
                number_of_episodes,
                status
                FROM nieszkolni_app_repertoireline
                WHERE status = 'not_in_stream'
                OR status = 'not_in_repertoire'
                ''')

            titles = cursor.fetchall()

            if len(titles) == 0:
                return None
            else:
                title = titles[0]
                return title

    def mark_repertoire_line_as_processed(self, stamp):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_repertoireline
                SET status = 'processed'
                WHERE stamp = {stamp}
                ''')

    def check_if_in_repertoire(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title
                FROM nieszkolni_app_repertoire
                WHERE title = '{title}'
                ''')

            title = cursor.fetchone()

            if title is None:
                return False
            else:
                return True

    def get_duration_from_repertoire(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                duration
                FROM nieszkolni_app_repertoire
                WHERE title = '{title}'
                ''')

            duration = cursor.fetchone()

            if duration is None:
                return None
            else:
                return duration[0]

    def display_titles(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title
                FROM nieszkolni_app_repertoire
                ''')

            titles = cursor.fetchall()

            return titles

    def add_notification(
            self,
            sender,
            recipient,
            subject,
            content,
            notification_type,
            status
            ):

        subject = Cleaner().clean_quotation_marks(subject)
        content = Cleaner().clean_quotation_marks(content)
        stamp = TimeMachine().now_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_notification (
                stamp,
                sender,
                recipient,
                subject,
                content,
                notification_type,
                status
                )
                VALUES (
                {stamp},
                '{sender}',
                '{recipient}',
                '{subject}',
                '{content}',
                '{notification_type}',
                '{status}'
                )
                ''')

    def display_announcements(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                notification_id,
                stamp,
                sender,
                recipient,
                subject,
                content,
                notification_type,
                status
                FROM nieszkolni_app_notification
                WHERE notification_type = 'visible_announcement'
                OR notification_type = 'hidden_announcement'
                ''')

            announcements = cursor.fetchall()

            return announcements

    def display_announcement(self, notification_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                notification_id,
                stamp,
                sender,
                recipient,
                subject,
                content,
                notification_type,
                status
                FROM nieszkolni_app_notification
                WHERE notification_id = '{notification_id}'
                ''')

            announcement = cursor.fetchone()

            return announcement

    def add_option(
            self,
            command,
            value,
            author
            ):

        stamp = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_option (
                stamp,
                date_number,
                command,
                value,
                author
                )
                VALUES (
                {stamp},
                {today_number},
                '{command}',
                '{value}',
                '{author}'
                )
                ''')

    def display_options(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                date_number,
                command,
                value,
                author,
                id
                FROM nieszkolni_app_option
                ''')

            options = cursor.fetchall()

            return options

    def remove_option(self, option_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_option
                WHERE id = {option_id}
                ''')

    def display_end_of_semester(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_option
                WHERE command = 'end_of_semester'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                end_of_semester = "SOON!"
            else:
                end_of_semester = data[0]

            return end_of_semester

