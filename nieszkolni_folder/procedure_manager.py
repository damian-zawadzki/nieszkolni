import os
import django

from django.db import connection

from nieszkolni_app.models import Curriculum


from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.sentence_manager import SentenceManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class ProcedureManager:
    def __init__(self):
        pass

    def contest_flashcards_vocabulary(
            self,
            start,
            end,
            method,
            threshold,
            reward,
            participants
            ):

        start_number = TimeMachine().date_to_number(start)
        end_number = TimeMachine().date_to_number(end)
        today_number = TimeMachine().today_number()

        days_left = end_number - today_number + 1

        pace = (end_number - start_number + 1) / threshold
        threshold_today = (today_number - start_number) * pace

        in_race = []
        out_of_race = []

        for participant in participants:
            result = StreamManager().studied_days(participant, start, end)

            if result >= threshold_today:
                in_race.append(participant)

        data = {
            "in_race": in_race,
            "out_of_race": out_of_race,
            "days_left": days_left
        }
        return data



