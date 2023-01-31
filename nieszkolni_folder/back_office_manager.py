import os
import django
from django.db import connection
from nieszkolni_app.models import Library
from nieszkolni_app.models import LibraryLine
from nieszkolni_app.models import Theater
from nieszkolni_app.models import RepertoireLine
from nieszkolni_app.models import Notification
from nieszkolni_app.models import Option
from nieszkolni_app.models import Store
from nieszkolni_app.models import Ticket
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.stream_manager import StreamManager

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
                '{position_number}',
                '{title}',
                '{wordcount}',
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

        check_if_in_library = self.check_if_in_library(link)

        if check_if_in_library is False:
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

    def next_postion_number(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT MAX(position_number)
                FROM nieszkolni_app_library
                WHERE position_number < 90000
                ''')

            last_postion_number = cursor.fetchone()

            if last_postion_number[0] is None:
                next_postion_number = 10000
                return next_postion_number

            else:
                next_postion_number = last_postion_number[0] + 1

                return next_postion_number

    def next_custom_postion_number(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT MAX(position_number)
                FROM nieszkolni_app_library
                WHERE position_number > 89999
                ''')

            last_custom_postion_number = cursor.fetchone()

            if last_custom_postion_number[0] is None:
                next_custom_postion_number = 90000
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

    def report_reading(self, client, link, current_user):
        check_if_in = self.check_if_in_library(link)

        if check_if_in is False:
            self.add_to_library_line(
                current_user,
                link,
                "reported"
                )
        else:
            wordcount = self.get_wordcount_from_library(link)

            StreamManager().add_to_stream(
                client,
                "PV",
                wordcount,
                current_user
                )

    # Theater and repertoire line

    def add_to_repertoire(
            self,
            title,
            duration,
            title_type
            ):

        title = Cleaner().clean_quotation_marks(title)
        check_if_in = self.check_if_in_repertoire(title)

        if check_if_in is False:
            with connection.cursor() as cursor:
                cursor.execute(f'''
                    INSERT INTO nieszkolni_app_theater (
                    title,
                    duration,
                    title_type
                    )
                    VALUES (
                    '{title}',
                    '{duration}',
                    '{title_type}'
                    )
                    ''')

    def delete_from_repertoire(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_theater
                WHERE title = '{title}'
                ''')

    def display_repertoire(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration,
                title_type
                FROM nieszkolni_app_theater
                ''')

            titles = cursor.fetchall()

            return titles

    def display_repertoire_position(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration,
                title_type
                FROM nieszkolni_app_theater
                WHERE title = '{title}'
                ''')

            title = cursor.fetchone()

            if title is None:
                return None
            else:
                title = title[0]

                return title

    def find_position_in_theater(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                duration,
                title_type
                FROM nieszkolni_app_theater
                WHERE id = '{unique_id}'
                ''')

            position = cursor.fetchone()

            return position

    def add_to_repertoire_line(
            self,
            name,
            title,
            number_of_episodes,
            status
            ):

        check_if_in = self.check_if_in_repertoire(title)

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
                LIMIT 1
                ''')

            position = cursor.fetchone()

            if position is None:
                return None
            else:

                stamp = position[0]
                date = position[1]
                client = position[2]
                title = position[3]
                number_of_episodes = position[4]
                status = position[5]

                check_if_in = self.check_if_in_repertoire(title)

                if check_if_in is True:
                    if status != "processed":

                        title_details = self.display_repertoire_position(title)
                        duration = title_details[1]
                        title_type = title_details[2]

                        self.process_repertoire_line(
                            title,
                            duration,
                            title_type,
                            position,
                            date
                            )

                        return self.display_reported_repertoire_line()

                return position

    def count_reported_repertoire_line(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(stamp)
                FROM nieszkolni_app_repertoireline
                WHERE status = 'not_in_stream'
                OR status = 'not_in_repertoire'
                ''')

            counter = cursor.fetchone()

            return counter[0]

    def process_repertoire_line(
            self,
            title,
            duration,
            title_type,
            position,
            date
            ):

        stamp = position[0]
        client = position[2]
        number_of_episodes = position[4]
        status = position[5]

        check_if_in = self.check_if_in_repertoire(title)

        if check_if_in is False:
            self.add_to_repertoire(
                title,
                duration,
                title_type
                )

        if status == "not_in_stream":
            self.report_listening(
                client,
                title,
                number_of_episodes,
                "automatic",
                date
                )

            self.mark_repertoire_line_as_processed(stamp)

    def mark_repertoire_line_as_processed(self, stamp):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_repertoireline
                SET status = 'processed'
                WHERE stamp = '{stamp}'
                ''')

    def remove_from_repertoire_line(self, stamp):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_repertoireline
                WHERE stamp = '{stamp}'
                ''')

    def check_if_in_repertoire(self, title):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title
                FROM nieszkolni_app_theater
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
                FROM nieszkolni_app_theater
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
                FROM nieszkolni_app_theater
                ''')

            titles = cursor.fetchall()

            return titles

    def report_listening(
            self,
            client,
            title,
            number_of_episodes,
            current_user,
            date
            ):

        check_if_in = self.check_if_in_repertoire(title)

        if check_if_in is False:
            self.add_to_repertoire_line(
                client,
                title,
                number_of_episodes,
                "not_in_stream"
                )
        else:
            StreamManager().add_to_stream_with_date(
                client,
                "PO",
                f'{title} *{number_of_episodes}',
                current_user,
                date
                )

    # Notifications
    def add_notifications(
            self,
            sender,
            recipients,
            subject,
            content,
            notification_type,
            status
            ):

        if recipients[0] == "all":
            self.add_notification(
                sender,
                recipients[0],
                subject,
                content,
                notification_type,
                status
                )
        else:
            for recipient in recipients:
                self.add_notification(
                    sender,
                    recipient,
                    subject,
                    content,
                    notification_type,
                    status
                    )

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
                WHERE notification_type != 'comment'
                ORDER BY stamp DESC
                ''')

            announcements = cursor.fetchall()

            return announcements

    def display_latest_announcements(self):
        now_number = TimeMachine().today_number()
        seven_days_ago_stamp = now_number - 604800

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
                WHERE (
                notification_type = 'visible_announcement'
                OR notification_type = 'article'
                OR notification_type = 'rule'
                )
                AND stamp >= {seven_days_ago_stamp}
                ORDER BY stamp DESC
                ''')

            announcements = cursor.fetchall()

            return announcements

    def display_latest_announcements_for_client(self, client):
        now_number = TimeMachine().today_number()
        seven_days_ago_stamp = now_number - 604800

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
                WHERE (
                notification_type = 'visible_announcement'
                OR notification_type = 'article'
                OR notification_type = 'rule'
                )
                AND stamp >= {seven_days_ago_stamp}
                AND (recipient = '{client}'
                OR recipient = 'all')
                ORDER BY stamp DESC
                ''')

            announcements = cursor.fetchall()

            return announcements

    def display_rules(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                notification_id,
                subject
                FROM nieszkolni_app_notification
                WHERE notification_type = 'rule'
                ORDER BY stamp DESC
                ''')

            rules = cursor.fetchall()

            return rules

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

    def update_notifications(
            self,
            notification_id,
            subject,
            content,
            notification_type
            ):

        subject = Cleaner().clean_quotation_marks(subject)
        content = Cleaner().clean_quotation_marks(content)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_notification
                SET
                subject = '{subject}',
                content = '{content}',
                notification_type = '{notification_type}'
                WHERE notification_id = '{notification_id}'
                ''')

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

    def countdown_end_of_semester(self):
        end = self.display_end_of_semester()
        end_number = TimeMachine().date_to_number(end)
        today_number = TimeMachine().today_number()

        end_week = TimeMachine().number_to_week(end_number)
        today_week = TimeMachine().number_to_week(today_number)
        countdown = end_week - today_week

        return countdown

    def display_start_of_semester(self):
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
                start_of_semester = "SOON!"
            else:
                start_of_semester = data[0]

            return start_of_semester

    def display_option_by_command(self, command):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT value
                FROM nieszkolni_app_option
                WHERE command = '{command}'
                ''')

            data = cursor.fetchone()

            if data is not None:
                data = data[0]

            return data

    def display_tags(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT command, value
                FROM nieszkolni_app_option
                WHERE command LIKE '%_tag'
                ''')

            items = cursor.fetchall()

            tags = dict()
            for item in items:
                tag = {item[0]: item[1]}
                tags.update(tag)

            return tags

# Store
    def add_to_store(
            self,
            watchword,
            cue,
            response
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_store (
                watchword,
                cue,
                response
                )
                VALUES (
                '{watchword}',
                '{cue}',
                '{response}'
                )
                ''')

    def display_from_store(self, watchword):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT cue, response
                FROM nieszkolni_app_store
                WHERE watchword = '{watchword}'
                ''')

            rows = cursor.fetchall()

            items = {row[0]: [] for row in rows}

            for row in rows:
                cue = row[0]
                responses = items[cue]
                responses.append(row[1])

            return items

    def reset_store(self, watchword):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_store
                WHERE watchword = '{watchword}'
                ''')

# Tickets
    def add_ticket(
            self,
            client,
            ticket_type,
            subject,
            description,
            assigned_user,
            responsible_user,
            status,
            sentiment,
            reporting_user
            ):

        subject = Cleaner().clean_quotation_marks(subject)
        description = Cleaner().clean_quotation_marks(description)

        stamp = TimeMachine().now_number()
        opening_date = TimeMachine().today_number()
        closing_date = 0
        response = ''
        comment = ''
        closing_stamp = 0
        response_time = 0

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_ticket (
                stamp,
                opening_date,
                closing_date,
                client,
                ticket_type,
                subject,
                description,
                reporting_user,
                assigned_user,
                responsible_user,
                status,
                sentiment,
                response,
                comment,
                closing_stamp,
                response_time
                )
                VALUES (
                '{stamp}',
                '{opening_date}',
                '{closing_date}',
                '{client}',
                '{ticket_type}',
                '{subject}',
                '{description}',
                '{reporting_user}',
                '{assigned_user}',
                '{responsible_user}',
                '{status}',
                '{sentiment}',
                '{response}',
                '{comment}',
                '{closing_stamp}',
                '{response_time}'
                )
                ''')

    def display_open_tickets(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                opening_date,
                closing_date,
                client,
                ticket_type,
                subject,
                description,
                reporting_user,
                assigned_user,
                responsible_user,
                status,
                sentiment,
                response,
                id,
                comment,
                closing_stamp,
                response_time
                FROM nieszkolni_app_ticket
                WHERE status != 'closed'
                ''')

            rows = cursor.fetchall()

            tickets = []
            if rows is not None:
                for row in rows:
                    ticket = {
                        "stamp": row[0],
                        "opening_date": TimeMachine().number_to_system_date(row[1]),
                        "closing_date": TimeMachine().number_to_system_date(row[2]),
                        "client": row[3],
                        "ticket_type": row[4],
                        "subject": row[5],
                        "description": row[6],
                        "reporting_user": row[7],
                        "assigned_user": row[8],
                        "responsible_user": row[9],
                        "status": row[10],
                        "sentiment": row[11],
                        "response": row[12],
                        "ticket_id": row[13],
                        "comment": row[14],
                        "closing_stamp": row[15],
                        "response_time": re.search(r"\d{1,2}", str(row[16])).group()
                        }

                    tickets.append(ticket)

            return tickets

    def display_closed_tickets(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                opening_date,
                closing_date,
                client,
                ticket_type,
                subject,
                description,
                reporting_user,
                assigned_user,
                responsible_user,
                status,
                sentiment,
                response,
                id,
                comment,
                closing_stamp,
                response_time
                FROM nieszkolni_app_ticket
                WHERE status = 'closed'
                ''')

            rows = cursor.fetchall()

            tickets = []
            if rows is not None:
                for row in rows:
                    ticket = {
                        "stamp": row[0],
                        "opening_date": TimeMachine().number_to_system_date(row[1]),
                        "closing_date": TimeMachine().number_to_system_date(row[2]),
                        "client": row[3],
                        "ticket_type": row[4],
                        "subject": row[5],
                        "description": row[6],
                        "reporting_user": row[7],
                        "assigned_user": row[8],
                        "responsible_user": row[9],
                        "status": row[10],
                        "sentiment": row[11],
                        "response": row[12],
                        "ticket_id": row[13],
                        "comment": row[14],
                        "closing_stamp": row[15],
                        "response_time": re.search(r"\d{1,2}", str(row[16])).group()
                        }

                    tickets.append(ticket)

            return tickets

    def display_ticket(self, ticket_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                opening_date,
                closing_date,
                client,
                ticket_type,
                subject,
                description,
                reporting_user,
                assigned_user,
                responsible_user,
                status,
                sentiment,
                response,
                id,
                comment,
                closing_stamp,
                response_time
                FROM nieszkolni_app_ticket
                WHERE id = '{ticket_id}'
                ''')

            row = cursor.fetchone()

            if row is not None:
                ticket = {
                    "stamp": row[0],
                    "opening_date": TimeMachine().number_to_system_date(row[1]),
                    "closing_date": TimeMachine().number_to_system_date(row[2]),
                    "client": row[3],
                    "ticket_type": row[4],
                    "subject": row[5],
                    "description": row[6],
                    "reporting_user": row[7],
                    "assigned_user": row[8],
                    "responsible_user": row[9],
                    "status": row[10],
                    "sentiment": row[11],
                    "response": row[12],
                    "ticket_id": row[13],
                    "comment": row[14],
                    "closing_stamp": row[15],
                    "response_time": re.search(r"\d{1,2}", str(row[16])).group()
                    }

            return ticket

    def assign_user_to_ticket(self, ticket_id, assigned_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_ticket
                SET assigned_user = '{assigned_user}'
                WHERE id = '{ticket_id}'
                ''')

    def change_ticket_status(self, ticket_id, status):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_ticket
                SET status = '{status}'
                WHERE id = '{ticket_id}'
                ''')

    def add_response_to_ticket(self, ticket_id, response):
        response = Cleaner().clean_quotation_marks(response)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_ticket
                SET response = '{response}'
                WHERE id = '{ticket_id}'
                ''')

    def close_ticket(self, ticket_id):
        ticket = self.display_ticket(ticket_id)
        opening_stamp = ticket["stamp"]

        closing_date = TimeMachine().today_number()
        closing_stamp = TimeMachine().now_number()
        response_time = (closing_stamp - opening_stamp)/3600

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_ticket
                SET
                closing_date = '{closing_date}',
                closing_stamp = '{closing_stamp}',
                response_time = '{response_time}'
                WHERE id = '{ticket_id}'
                ''')

    def comment_on_ticket(self, ticket_id, comment):
        comment = Cleaner().clean_quotation_marks(comment)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_ticket
                SET comment = '{comment}'
                WHERE id = '{ticket_id}'
                ''')
