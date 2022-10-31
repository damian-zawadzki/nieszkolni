import os
import django
from django.db import connection
from nieszkolni_app.models import SentenceStock
from nieszkolni_app.models import Set
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class SentenceManager:
    def __init__(self):
        pass

    def upload_sentence_stock(self, sentence_id, polish, english, glossary):
        polish = Cleaner().clean_quotation_marks(polish)
        english = Cleaner().clean_quotation_marks(english)
        glossary = Cleaner().clean_quotation_marks(glossary)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_sentencestock (
                sentence_id,
                polish,
                english,
                glossary
                ) VALUES (
                {sentence_id},
                '{polish}',
                '{english}',
                '{glossary}'
                )
                ON CONFLICT (sentence_id)
                DO NOTHING
                ''')

    def display_sentence_stock(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sentence_id, polish, english, glossary
                FROM nieszkolni_app_sentencestock
                ''')

            sentences = cursor.fetchall()

            return sentences

    def upload_sets(self, set_name, sentence_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_set (
                set_name,
                sentence_id
                ) VALUES (
                '{set_name}',
                {sentence_id}
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_set_names(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT set_name 
                FROM nieszkolni_app_set
                ORDER BY set_name
                ''')

            set_names_raw = cursor.fetchall()
            set_names = [set_name[0] for set_name in set_names_raw]

            return set_names

    def next_list_number(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT MAX(list_number)
                FROM nieszkolni_app_composer
                ''')

            last_list_number_raw = cursor.fetchone()
            last_list_number = last_list_number_raw[0]

            if last_list_number is None:
                next_list_number = 1000
                return next_list_number

            else:
                last_list_number = str(last_list_number)[0:4]
                next_list_number = int(last_list_number) + 1
                return next_list_number

    def compose_sentence_lists(self, name, set_name):
        next_list_number = self.next_list_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stock.sentence_id,
                stock.polish,
                stock.english,
                stock.glossary
                FROM nieszkolni_app_sentencestock stock
                INNER JOIN nieszkolni_app_set s
                ON s.sentence_id = stock.sentence_id
                WHERE s.set_name = '{set_name}'
                ''')

            entries = cursor.fetchall()

            list_of_sentences = []
            index = 1
            subindex = 1
            list_number = 0

            for entry in entries:
                list_number = f"{next_list_number}{index:02d}"
                sentence_number = f"{list_number}{subindex:02d}"

                list_of_sentences.append({
                    "list_number": list_number,
                    "sentence_number": int(sentence_number),
                    "sentence_id": entry[0],
                    "name": name,
                    "polish": entry[1],
                    "english": entry[2],
                    "glossary": entry[3]
                    })

                if subindex == 10:
                    subindex = 1
                    index += 1
                else:
                    subindex += 1

            self.plan_sentence_lists(list_of_sentences)
            return list_of_sentences

    def plan_sentence_lists(self, list_of_sentences):
        for sentence in list_of_sentences:
            list_number = sentence.get("list_number")
            sentence_number = sentence.get("sentence_number")
            sentence_id = sentence.get("sentence_id")
            name = sentence.get("name")
            polish = sentence.get("polish")
            english = sentence.get("english")
            glossary = sentence.get("glossary")
            submission_stamp = 0
            submission_date = 0
            status = "generated"
            translation = ""
            result = ""
            reviewing_user = ""

            with connection.cursor() as cursor:
                cursor.execute(f'''
                    INSERT INTO nieszkolni_app_composer (
                    list_number,
                    sentence_number,
                    sentence_id,
                    name,
                    polish,
                    english,
                    glossary,
                    submission_stamp,
                    submission_date,
                    status,
                    translation,
                    result,
                    reviewing_user
                    )
                    VALUES (
                    {list_number},
                    {sentence_number},
                    {sentence_id},
                    '{name}',
                    '{polish}',
                    '{english}',
                    '{glossary}',
                    {submission_stamp},
                    {submission_date},
                    '{status}',
                    '{translation}',
                    '{result}',
                    '{reviewing_user}'
                    )
                    ON CONFLICT (sentence_number)
                    DO NOTHING
                    ''')

    def display_planned_sentences_per_student(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                status,
                list_number,
                sentence_number,
                sentence_id,
                name,
                polish,
                english,
                glossary
                FROM nieszkolni_app_composer
                WHERE name = '{name}'
                ''')

            sentences = cursor.fetchall()

            return sentences

    def display_planned_sentence_lists_per_student(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT list_number
                FROM nieszkolni_app_composer
                WHERE name = '{name}'
                AND status = 'generated'
                ''')

            entries = cursor.fetchall()

            return entries

    def display_sentence_list(self, list_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                sentence_number,
                polish
                FROM nieszkolni_app_composer
                WHERE list_number = {list_number}
                ''')

            sentences = cursor.fetchall()
            print(sentences)
            return sentences

    def mark_sentence_list_as_planned(self, list_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_composer
                SET status = "planned"
                WHERE list_number = {list_number}
                ''')

    def submit_sentence_translation(self, translations):
        now_number = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        for translation in translations:
            sentence_number = translation[0]
            answer = translation[1]

            with connection.cursor() as cursor:
                cursor.execute(f'''
                    UPDATE nieszkolni_app_composer
                    SET
                    submission_stamp = {now_number},
                    submission_date = {today_number},
                    status = 'translated',
                    translation = '{answer}'
                    WHERE sentence_number = {sentence_number}
                    ''')

    def display_sentences_to_grade(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                polish,
                english,
                translation,
                sentence_number
                FROM nieszkolni_app_composer
                WHERE result = ''
                ''')

            entries = cursor.fetchall()
            if len(entries) == 0:
                return None
            else:
                entry = entries[0]
                return entry

    def grade_sentence(self, sentence_number, result, reviewing_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_composer
                SET
                status = 'graded',
                result = '{result}',
                reviewing_user = '{reviewing_user}'
                WHERE sentence_number = {sentence_number}
                ''')

    def display_graded_list(self, list_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                result,
                polish,
                translation
                FROM nieszkolni_app_composer
                WHERE list_number = {list_number}
                ''')

            entries = cursor.fetchall()

            return entries

    def display_list_status(self, list_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                status
                FROM nieszkolni_app_composer
                WHERE list_number = {list_number}
                ''')

            status = cursor.fetchone()

            return status