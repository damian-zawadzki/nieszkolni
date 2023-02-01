import os
import django

from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
                maximal_interval_sentences,
                wage
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
                '90',
                '60'
                )
                ON CONFLICT (name)
                DO NOTHING
                ''')

    def add_client_and_user(self, f_name, l_name, password, user):
        system_username = f_name.lower() + l_name.lower()
        username = f_name + " " + l_name
        internal_email_address = "-"

        if user is None:
            user = User.objects.create_user(
                    system_username,
                    internal_email_address,
                    password
                    )

            user.first_name = f_name
            user.last_name = l_name

            is_client = ClientsManager().verify_client(username)
            if is_client is False:

                try:
                    ClientsManager().add_client(
                        username,
                        internal_email_address
                        )

                    user.save()

                except Exception as e:
                    messages = "There has been a mistake. Contact the administration team."
                    product = ("ERROR", message, "register_user")

                    return product

                message = "The user has been added to the database."
                product = ("SUCCESS", message, "list_current_users")
                return product

            else:
                message = "The student already exists."
                product = ("WARNING", message, "register_user")
                return product

        else:
            message = "The student already exists."
            product = ("WARNING", message, "register_user")
            return product

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
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_client
                WHERE status = 'active'
                ORDER BY name ASC
                ''')

            users = cursor.fetchall()

            current_users = [user[0] for user in users]

            return current_users

    def list_current_clients(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_client
                WHERE status = 'active'
                AND user_type = 'client'
                ORDER BY name ASC
                ''')

            clients = cursor.fetchall()

            current_clients = [client[0] for client in clients]

            return current_clients

    def list_current_staff(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_client
                WHERE status = 'active'
                AND (user_type = 'staff' OR user_type = 'coach')
                ORDER BY name ASC
                ''')

            employees = cursor.fetchall()

            current_employees = [employee[0] for employee in employees]

            return current_employees

    def list_current_coaches(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_client
                WHERE status = 'active'
                AND user_type = 'coach'
                ORDER BY name ASC
                ''')

            employees = cursor.fetchall()

            current_employees = [employee[0] for employee in employees]

            return current_employees

    def list_all_users(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_client
                ORDER BY name ASC
                ''')

            rows = cursor.fetchall()

            clients = [row[0] for row in rows]

            return clients

    def load_user(self, name):
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
                maximal_interval_sentences,
                wage
                FROM nieszkolni_app_client
                WHERE name = '{name}'
                ''')

            details = cursor.fetchone()

            entry = {
                "user_type": details[0],
                "name": details[1],
                "phone_number": details[2],
                "contact_email_address": details[3],
                "school": details[4],
                "internal_email_address": details[5],
                "meeting_duration": details[6],
                "price": details[7],
                "acquisition_channel": details[8],
                "recommenders": details[9],
                "reasons_for_resignation": details[10],
                "status": details[11],
                "coach": details[12],
                "level": details[13],
                "daily_limit_of_new_vocabulary": details[14],
                "maximal_interval_vocabulary": details[15],
                "daily_limit_of_new_sentences": details[16],
                "maximal_interval_sentences": details[17],
                "wage": details[18]
            }

            return entry

    def edit_user(
            self,
            user_type,
            name,
            phone_number,
            contact_email_address,
            meeting_duration,
            acquisition_channel,
            recommenders,
            reasons_for_resignation,
            status,
            coach,
            level,
            daily_limit_of_new_vocabulary,
            maximal_interval_vocabulary,
            daily_limit_of_new_sentences,
            maximal_interval_sentences,
            wage
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_client
                SET
                user_type = '{user_type}',
                name = '{name}',
                phone_number = {phone_number},
                contact_email_address = '{contact_email_address}',
                meeting_duration = {meeting_duration},
                acquisition_channel = '{acquisition_channel}',
                recommenders = '{recommenders}',
                reasons_for_resignation = '{reasons_for_resignation}',
                status = '{status}',
                coach = '{coach}',
                level = '{level}',
                daily_limit_of_new_vocabulary = '{daily_limit_of_new_vocabulary}',
                maximal_interval_vocabulary = '{maximal_interval_vocabulary}',
                daily_limit_of_new_sentences = '{daily_limit_of_new_sentences}',
                maximal_interval_sentences = '{daily_limit_of_new_sentences}',
                wage = '{wage}'
                WHERE name = '{name}'
                ''')

    def get_coach_by_client(self, client):
        client = Client.objects.get(name=client)
        coach = client.coach

        return coach