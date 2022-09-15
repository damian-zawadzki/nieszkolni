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
            test_user,
            name,
            phone_number,
            contact_email_address,
            school,
            internal_email_address,
            meeting_duration,
            price,
            acquisition_channel,
            recommenders,
            coach,
            level
            ):

        entry = Client()
        entry.test_user = test_user
        entry.name = name
        entry.phone_number = phone_number
        entry.contact_email_address = contact_email_address
        entry.school = school
        entry.internal_email_address = internal_email_address
        entry.meeting_duration = meeting_duration
        entry.price = price
        entry.acquisition_channel = acquisition_channel
        entry.recommenders = recommenders
        entry.status = "course_started"
        entry.coach = coach
        entry.level = level
        entry.save()

        return "The client has been added to the system."

    def verify_client(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client WHERE name = '{name}'")
            names = cursor.fetchall()

            if len(names) == 0:
                return False
            else:
                return True

    def list_current_clients(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_client WHERE status = 'course_started'")
            clients = cursor.fetchall()

            current_clients = [client[0] for client in clients]

            return current_clients

