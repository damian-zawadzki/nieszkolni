import os
import django
from django.db import connection
from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.sentence_manager import SentenceManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.vocabulary_manager import VocabularyManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class AuditManager:
    def __init__(self):
        pass

    # Audit
    def clock_in(
            self,
            category_display_name,
            remarks,
            clocking_user,
            entry_type,
            tags
            ):

        stamp = TimeMachine().now_number()
        clock_in = stamp
        clock_out = 0
        duration = 0
        category = self.find_category_by_display_name(category_display_name)
        category_number = category["category_number"]
        category_name = category["category_name"]
        category_value = category["category_value"]
        date_number = TimeMachine().today_number()
        remarks = Cleaner().clean_quotation_marks(remarks)
        status = "started"
        tags = Cleaner().clean_quotation_marks(tags)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_audit (
                stamp,
                clock_in,
                clock_out,
                duration,
                category_number,
                category_name,
                date_number,
                remarks,
                status,
                clocking_user,
                entry_type,
                category_value,
                tags
                )
                VALUES (
                '{stamp}',
                '{clock_in}',
                '{clock_out}',
                '{duration}',
                '{category_number}',
                '{category_name}',
                '{date_number}',
                '{remarks}',
                '{status}',
                '{clocking_user}',
                '{entry_type}',
                '{category_value}',
                '{tags}'
                )
                ''')

    def clock_in_out(
            self,
            clock_in,
            clock_out,
            category_display_name,
            remarks,
            clocking_user,
            entry_type,
            tags
            ):

        stamp = TimeMachine().now_number()
        clock_in = TimeMachine().date_time_to_number(clock_in)
        clock_out = TimeMachine().date_time_to_number(clock_out)
        duration = clock_out - clock_in

        category = self.find_category_by_display_name(category_display_name)
        category_number = category["category_number"]
        category_name = category["category_name"]
        category_value = category["category_value"]
        date_number = TimeMachine().time_number_to_date_number(clock_in)
        remarks = Cleaner().clean_quotation_marks(remarks)
        status = "awaiting"
        tags = Cleaner().clean_quotation_marks(tags)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_audit (
                stamp,
                clock_in,
                clock_out,
                duration,
                category_number,
                category_name,
                date_number,
                remarks,
                status,
                clocking_user,
                entry_type,
                category_value,
                tags
                )
                VALUES (
                '{stamp}',
                '{clock_in}',
                '{clock_out}',
                '{duration}',
                '{category_number}',
                '{category_name}',
                '{date_number}',
                '{remarks}',
                '{status}',
                '{clocking_user}',
                '{entry_type}',
                '{category_value}',
                '{tags}'
                )
                ''')

    def upload_timesheet(
            self,
            stamp,
            clock_in,
            clock_out,
            duration,
            category_number,
            category_name,
            date_number,
            remarks,
            status,
            clocking_user,
            entry_type,
            category_value,
            tags
            ):

        stamp = TimeMachine().date_time_to_number(stamp)
        clock_in = TimeMachine().date_time_to_number(clock_in)
        clock_out = TimeMachine().date_time_to_number(clock_out)
        date_number = TimeMachine().date_to_number(date_number)
        category_name = Cleaner().clean_quotation_marks(category_name)
        remarks = Cleaner().clean_quotation_marks(remarks)
        tags = Cleaner().clean_quotation_marks(tags)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_audit (
                stamp,
                clock_in,
                clock_out,
                duration,
                category_number,
                category_name,
                date_number,
                remarks,
                status,
                clocking_user,
                entry_type,
                category_value,
                tags
                )
                VALUES (
                '{stamp}',
                '{clock_in}',
                '{clock_out}',
                '{duration}',
                '{category_number}',
                '{category_name}',
                '{date_number}',
                '{remarks}',
                '{status}',
                '{clocking_user}',
                '{entry_type}',
                '{category_value}',
                '{tags}'
                )
                ''')

    def clock_out(self, clocking_user):

        current_entry = self.current_entry(clocking_user)
        current_entry_id = current_entry[0]
        clock_in = current_entry[2]
        clock_out = TimeMachine().now_number()
        duration = clock_out - int(clock_in)
        status = "finished"

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_audit
                SET
                clock_in = '{clock_in}',
                clock_out = '{clock_out}',
                duration = '{duration}',
                status = '{status}'
                WHERE id = '{current_entry_id}'
                ''')

    def remove_entry(self, clocking_user, stamp):
        stamp = TimeMachine().date_time_to_number(stamp)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_audit
                WHERE clocking_user = '{clocking_user}'
                AND stamp = '{stamp}'
                ''')

    def check_if_clocked_in(self, clocking_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT clock_out
                FROM nieszkolni_app_audit
                WHERE clocking_user = '{clocking_user}'
                AND entry_type = 'automatic'
                AND status = 'started'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            response = cursor.fetchone()

            if response is not None:
                if response[0] == 0:
                    status = True
                else:
                    status = False
            else:
                status = False

            return status

    def current_entry(self, clocking_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                clock_in,
                clock_out,
                duration,
                category_number,
                category_name,
                date_number,
                remarks,
                status,
                clocking_user,
                entry_type,
                category_value,
                tags
                FROM nieszkolni_app_audit
                WHERE clocking_user = '{clocking_user}'
                AND entry_type = 'automatic'
                AND status = 'started'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            entry = cursor.fetchone()

            return entry

    def display_entries(self, clocking_user, start, end):
        start_number = TimeMachine().date_to_number(start)
        end_number = TimeMachine().date_to_number(end)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                clock_in,
                clock_out,
                duration,
                category_number,
                category_name,
                date_number,
                remarks,
                status,
                clocking_user,
                entry_type,
                category_value,
                tags
                FROM nieszkolni_app_audit
                WHERE date_number >= '{start_number}'
                AND date_number <= '{end_number}'
                AND clocking_user = '{clocking_user}'
                ORDER BY stamp DESC
                ''')

            rows = cursor.fetchall()

            entries = []
            for row in rows:
                status = row[9]
                category_name = row[6]

                if status == "awaiting":
                    category_name = f"<b><b>Awaiting approval: </b></b>{category_name}"

                entry = {
                    "entry_id": row[0],
                    "stamp": row[1],
                    "clock_in": TimeMachine().number_to_system_date_time(row[2]),
                    "clock_out": TimeMachine().number_to_system_date_time(row[3]),
                    "duration": self.convert_to_h_min(round(int(row[4])/60)),
                    "category_number": row[5],
                    "category_name": category_name,
                    "date_number":  TimeMachine().number_to_system_date(row[7]),
                    "remarks": row[8],
                    "status": status,
                    "clocking_user": row[10],
                    "entry_type": row[11],
                    "category_value": row[12],
                    "tags": row[13]
                    }

                entries.append(entry)

            return entries

    def display_total_duration_min(self, entries):
        duration_entries = [
            self.convert_to_min_from_h_min(entry["duration"])
            for entry in entries
            ]

        duration = sum(duration_entries)

        return duration

    def display_total_duration_h_min(self, entries):
        duration_raw = self.display_total_duration_min(entries)
        duration = self.convert_to_h_min(duration_raw)

        return duration

    def convert_to_h_min(self, duration):
        duration = int(duration)

        hours = duration // 60
        minutes = duration % 60

        result = f"{hours}h {minutes}min"

        return result

    def convert_to_min_from_h_min(self, duration):
        hours_text = re.search(r"\d{1,}h", duration).group()
        hours = int(re.sub("h", "", hours_text))

        minutes_text = re.search(r"\s\d{1,}min", duration).group()
        minutes = int(re.sub(r"\s|min", "", minutes_text))

        duration = (hours * 60) + minutes

        return duration


    # Category
    def add_category(
            self,
            category_name,
            category_display_name,
            category_number,
            category_value
            ):

        category_name = Cleaner().clean_quotation_marks(category_name)
        category_display_name = Cleaner().clean_quotation_marks(category_display_name)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_category (
                category_name,
                category_display_name,
                category_number,
                category_value
                )
                VALUES (
                '{category_name}',
                '{category_display_name}',
                '{category_number}',
                '{category_value}'
                )
                ''')

    def add_category_display_name(
            self,
            category_name,
            category_display_name
            ):

        category_name = Cleaner().clean_quotation_marks(category_name)
        category_display_name = Cleaner().clean_quotation_marks(category_display_name)

        category = self.find_category_by_name(category_name)
        category_number = category["category_number"]
        category_value = category["category_value"]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_category (
                category_name,
                category_display_name,
                category_number,
                category_value
                )
                VALUES (
                '{category_name}',,
                '{category_display_name}',,
                '{category_number}',,
                '{category_value}'
                )
                ''')

    def display_categories(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                category_name,
                category_display_name,
                category_number,
                category_value
                FROM nieszkolni_app_category
                ORDER BY category_display_name ASC
                ''')

            categories = cursor.fetchall()

            return categories

    def display_category_names(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT category_name
                FROM nieszkolni_app_category
                ''')

            categories = cursor.fetchall()

            return categories

    def find_category_by_name(self, category_name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                category_number,
                category_value
                FROM nieszkolni_app_category
                WHERE category_name = '{category_name}'
                LIMIT 1
                ''')

            data = cursor.fetchone()

            category = dict()
            if data is not None:
                category.update({"category_number": data[2]})
                category.update({"category_value": data[1]})

            return category

    def find_category_by_display_name(self, category_display_name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                category_number,
                category_name,
                category_value
                FROM nieszkolni_app_category
                WHERE category_display_name = '{category_display_name}'
                ''')

            data = cursor.fetchone()

            category = dict()
            if data is not None:
                category.update({"category_number": data[0]})
                category.update({"category_name": data[1]})
                category.update({"category_value": data[2]})

            return category
