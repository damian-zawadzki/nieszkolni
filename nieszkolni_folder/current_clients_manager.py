import os
import django
from django.db import connection
from nieszkolni_app.models import CurrentClient
from nieszkolni_folder.time_machine import TimeMachine


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class CurrentClientsManager:
    def __init__(self):
        pass

    def current_client(self, coach):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM nieszkolni_app_currentclient WHERE coach = '{coach}'")
            current_client = cursor.fetchone()
            
            if current_client is None:
                current_client = ""
            else:
                current_client = current_client[0]
                
            return current_client

    def switch_current_client(self, coach, client):
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO nieszkolni_app_currentclient (coach, name) VALUES ('{coach}', '{client}') ON CONFLICT (coach) DO UPDATE SET name = '{client}'")