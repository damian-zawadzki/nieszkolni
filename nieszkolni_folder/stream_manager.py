import os
import django
from django.db import connection
from nieszkolni_app.models import Stream
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

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

    def display_stream(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT stamp, date_number, date, name, command, value, stream_user, status, id
                FROM nieszkolni_app_stream
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