import os
import django
from django.db import connection
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.back_office_manager import BackOfficeManager
from nieszkolni_folder.stream_manager import StreamManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class BackOfficePlanner:
    def __init__(self):
        pass

    def report_reading(self, client, link, current_user):
        check_if_in = BackOfficeManager().check_if_in_library(link)

        if check_if_in is False:
            BackOfficeManager().add_to_library_line(
                current_user,
                link,
                "reported"
                )
        else:
            wordcount = BackOfficeManager().get_wordcount_from_library(link)

            self().add_to_stream(
                client,
                "PV",
                wordcount,
                current_user
                )

    def report_listening(
            self,
            client,
            title,
            number_of_episodes,
            current_user
            ):

        check_if_in = BackOfficeManager().check_if_in_repertoire(title)

        if check_if_in is False:
            BackOfficeManager().add_to_repertoire_line(
                client,
                title,
                number_of_episodes,
                "not_in_stream"
                )
        else:
            self.add_to_stream(
                client,
                "PO",
                f'{title} *{number_of_episodes}',
                current_user
                )

    def process_repertoire_line(
            self,
            title,
            duration,
            title_type,
            position
            ):

        stamp = position[0]
        client = position[2]
        number_of_episodes = position[4]
        status = position[5]

        check_if_in = BackOfficeManager().check_if_in_repertoire(title)

        if check_if_in is False:
            BackOfficeManager().add_to_repertoire(
                title,
                duration,
                title_type
                )

        if status == "not_in_stream":
            self.report_listening(
                client,
                title,
                number_of_episodes,
                "automatic"
                )

            BackOfficeManager().mark_repertoire_line_as_processed(stamp)