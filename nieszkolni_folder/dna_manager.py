import os
import django

from django.db import connection

from nieszkolni_app.models import Stream

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class DnaManager:
    def __init__(self):
        pass

    def new_cards(self, coach, client, deck, start=None, end=None):
        pass