import os
import django
from django.db import connection
from nieszkolni_app.models import Client
from nieszkolni_folder.time_machine import TimeMachine


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class ClientsManager:
    def __init__(self):
        pass

    def add_client(
            self,
            name,
            internal_email_address
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_client (
                user_type,
                name,
                phone_number,
                contact_email_address,
                school,
                internal_email_address,
                meeting_duration,
                price,
                acquisition_channel,
                recommenders,
                reasons_for_resignation,
                status,
                coach,
                level,
                daily_limit_of_new_vocabulary,
                maximal_interval_vocabulary,
                daily_limit_of_new_sentences,
                maximal_interval_sentences
                )
                VALUES (
                'client',
                '{name}',
                987654321,
                '-',
                '-',
                '{internal_email_address}',
                55,
                0,
                '-',
                '-',
                '-',
                'active',
                '-',
                '-',
                '25',
                '90',
                '25',
                '90'
                )
                ON CONFLICT (name)
                DO NOTHING
                ''')

    def verify_client(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client WHERE name = '{name}'")
            names = cursor.fetchall()

            if len(names) == 0:
                return False
            else:
                return True

    def list_current_users(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client")
            users = cursor.fetchall()

            current_users = [user[0] for user in users]

            return current_users

    def list_current_clients(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client WHERE status = 'active' AND user_type = 'client'")
            clients = cursor.fetchall()

            current_clients = [client[0] for client in clients]

            return current_clients

    def list_current_staff(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client WHERE status = 'active' AND user_type = 'staff'")
            employees = cursor.fetchall()

            current_employees = [employee[0] for employee in employees]

            return current_employees

    def load_client(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                user_type,
                name,
                phone_number,
                contact_email_address,
                school,
                internal_email_address,
                meeting_duration,
                price,
                acquisition_channel,
                recommenders,
                reasons_for_resignation,
                status,
                coach,
                level,
                daily_limit_of_new_vocabulary,
                maximal_interval_vocabulary,
                daily_limit_of_new_sentences,
                maximal_interval_sentences
                FROM nieszkolni_app_client
                WHERE name = '{name}'
                ''')

            client_details = cursor.fetchone()

            return client_details

    def edit_client(
            self,
            user_type,
            name,
            phone_number,
            contact_email_address,
            internal_email_address,
            meeting_duration,
            price,
            acquisition_channel,
            recommenders,
            reasons_for_resignation,
            status,
            coach,
            level,
            daily_limit_of_new_vocabulary,
            maximal_interval_vocabulary,
            daily_limit_of_new_sentences,
            maximal_interval_sentences
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_client
                SET
                user_type = '{user_type}',
                name = '{name}',
                phone_number = {phone_number},
                contact_email_address = '{contact_email_address}',
                internal_email_address = '{internal_email_address}',
                meeting_duration = {meeting_duration},
                price = {price},
                acquisition_channel = '{acquisition_channel}',
                recommenders = '{recommenders}',
                reasons_for_resignation = '{reasons_for_resignation}',
                status = '{status}',
                coach = '{coach}',
                level = '{level}',
                daily_limit_of_new_vocabulary = '{daily_limit_of_new_vocabulary}',
                maximal_interval_vocabulary = '{maximal_interval_vocabulary}',
                daily_limit_of_new_sentences = '{daily_limit_of_new_sentences}',
                maximal_interval_sentences = '{daily_limit_of_new_sentences}'
                WHERE name = '{name}'
                ''')