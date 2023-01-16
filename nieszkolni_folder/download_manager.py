import os
import django
from django.db import connection
from django.conf import settings as django_settings
from django.http import HttpResponse

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

from nieszkolni_folder.document_manager import DocumentManager
from nieszkolni_folder.submission_manager import SubmissionManager
from nieszkolni_folder.sentence_manager import SentenceManager

import re
from io import BytesIO
from zipfile import ZipFile

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class DownloadManager:

    def __init__(self):
        pass

    def download_assignments(self, start_date, end_date):

        file_paths = []

        assignments = SubmissionManager().download_graded_assignments(
            start_date,
            end_date
            )

        # Assignments
        for assignment in assignments:
            date = assignment[0]
            item = assignment[1]
            name = assignment[2]
            title = assignment[3]
            wordcount = assignment[4]
            flagged_content = assignment[5]
            minor_errors = assignment[6]
            major_errors = assignment[7]
            reviewing_user = assignment[8]
            comment = assignment[9]
            grade = assignment[10]
            assignment_type = assignment[11]

            path = DocumentManager().create_assignment_doc(
                date,
                item,
                name,
                title,
                wordcount,
                flagged_content,
                minor_errors,
                major_errors,
                reviewing_user,
                comment,
                grade
                )

            file_path = os.path.join(django_settings.MEDIA_ROOT, path)
            file_paths.append((path, file_path))

        # Sentences
        sentence_lists_raw = SentenceManager().download_graded_sentence_lists(
            start_date,
            end_date
            )

        sentence_lists = list(sentence_lists_raw.values())

        for sentence_list in sentence_lists:
            path = DocumentManager().create_sentences_doc(sentence_list)

            file_path = os.path.join(django_settings.MEDIA_ROOT, path)
            file_paths.append((path, file_path))

        zone = BytesIO()
        zip_file = ZipFile(zone, "w")

        for file_path in file_paths:
            zip_file.write(file_path[1], file_path[0])

        zip_file.close()

        response = HttpResponse(zone.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % "assignments.zip"

        return response

    def download_document(self, path):

        file_path = os.path.join(django_settings.MEDIA_ROOT, path)

        with open(file_path, 'rb') as file:

            response = HttpResponse(file.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)

            return response