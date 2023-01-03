import os
import django
from django.db import connection
from nieszkolni_app.models import SentenceStock
from nieszkolni_app.models import Set
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

from nieszkolni_folder.knowledge_manager import KnowledgeManager

from copy import deepcopy
import json

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
                )
                VALUES (
                '{sentence_id}',
                '{polish}',
                '{english}',
                '{glossary}'
                )
                ON CONFLICT (sentence_id)
                DO NOTHING
                ''')

    def update_sentence_stock(self, sentence_id, polish, english, glossary):
        polish = Cleaner().clean_quotation_marks(polish)
        english = Cleaner().clean_quotation_marks(english)
        glossary = Cleaner().clean_quotation_marks(glossary)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_sentencestock
                SET
                polish = '{polish}',
                english = '{english}',
                glossary = '{glossary}'
                WHERE sentence_id = '{sentence_id}'
                ''')

    def display_sentence_stock(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sentence_id, polish, english, glossary
                FROM nieszkolni_app_sentencestock
                ''')

            sentences = cursor.fetchall()

            return sentences

    def display_sentence_stock_json(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sentence_id, polish, english, glossary
                FROM nieszkolni_app_sentencestock
                ''')

            sentences = cursor.fetchall()

            entries = dict()
            for sentence in sentences:
                value = {
                    "polish": sentence[1],
                    "english": sentence[2],
                    "glossary": sentence[3],
                }

                key = sentence[0]
                entries.update({key: value})

            # sentences_json = json.dumps(entries)

            return entries

    def display_next_sentence_id(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sentence_id
                FROM nieszkolni_app_sentencestock
                ORDER BY sentence_id DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                next_sentence_id = 10001
            else:
                next_sentence_id = int(data[0]) + 1

            return next_sentence_id

    def display_sentences_by_id(self, sentence_ids):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sentence_id, polish, english, glossary
                FROM nieszkolni_app_sentencestock
                WHERE sentence_id IN ({sentence_ids})
                ''')

            sentences = cursor.fetchall()

            return sentences

    def add_set(self, set_id, set_name, sentence_ids, set_type):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_set (
                set_id,
                set_name,
                sentence_ids,
                set_type
                )
                VALUES (
                '{set_id}',
                '{set_name}',
                '{sentence_ids}',
                '{set_type}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_next_set_id(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT set_id
                FROM nieszkolni_app_set
                ORDER BY set_id DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                next_set_id = 10000
            else:
                next_set_id = int(data[0]) + 1

            return next_set_id

    def display_all_sets(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT set_id, set_name, set_type
                FROM nieszkolni_app_set
                ORDER BY set_id
                ''')

            sets = cursor.fetchall()

            return sets

    def display_sets_by_type(self, set_type):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT set_id, set_name, set_type
                FROM nieszkolni_app_set
                WHERE set_type = '{set_type}'
                ORDER BY set_id
                ''')

            sets = cursor.fetchall()

            return sets

    def display_set(self, set_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT set_id, set_name, sentence_ids
                FROM nieszkolni_app_set
                WHERE set_id = '{set_id}'
                ''')

            set_details = cursor.fetchone()

            return set_details

    def remove_set(self, set_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_set
                WHERE set_id = '{set_id}'
                ''')

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

    def compose_sentence_lists(self, name, item, set_id, sentence_ids):
        next_list_number = self.next_list_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                sentence_id,
                polish,
                english,
                glossary
                FROM nieszkolni_app_sentencestock
                WHERE sentence_id IN ({sentence_ids})
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
                    "glossary": entry[3],
                    "set_id": set_id,
                    "item": item
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
            status = "planned"
            translation = ""
            result = ""
            reviewing_user = ""
            set_id = sentence.get("set_id")
            item = sentence.get("item")

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
                    reviewing_user,
                    set_id,
                    item
                    )
                    VALUES (
                    '{list_number}',
                    '{sentence_number}',
                    '{sentence_id}',
                    '{name}',
                    '{polish}',
                    '{english}',
                    '{glossary}',
                    '{submission_stamp}',
                    '{submission_date}',
                    '{status}',
                    '{translation}',
                    '{result}',
                    '{reviewing_user}',
                    '{set_id}',
                    '{item}'
                    )
                    ON CONFLICT (sentence_number)
                    DO NOTHING
                    ''')

            if glossary is not None:
                number_of_phrases = glossary.count("/")
                if number_of_phrases >= 1:
                    phrases = glossary.split("/")
                elif number_of_phrases < 1:
                    phrases = []
                    phrases.append(glossary)

                for phrase in phrases:
                    KnowledgeManager().add_to_book(
                        name,
                        phrase,
                        "system",
                        "vocabulary"
                        )

    def find_list_number_by_item(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT list_number
                FROM nieszkolni_app_composer
                WHERE item = '{item}'
                ''')

            list_number = cursor.fetchone()

            if list_number is not None:
                list_number = list_number[0]

            return list_number

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
            answer = Cleaner().clean_quotation_marks(answer)

            with connection.cursor() as cursor:
                cursor.execute(f'''
                    UPDATE nieszkolni_app_composer
                    SET
                    submission_stamp = '{now_number}',
                    submission_date = '{today_number}',
                    status = 'translated',
                    translation = '{answer}'
                    WHERE sentence_number = '{sentence_number}'
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
                WHERE status = 'translated'
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

    def download_graded_sentence_lists(self, start_date, end_date):
        start = TimeMachine().date_to_number(start_date)
        end = TimeMachine().date_to_number(end_date)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                result,
                polish,
                translation,
                list_number,
                name,
                submission_date,
                reviewing_user,
                item
                FROM nieszkolni_app_composer
                WHERE status = 'graded'
                AND submission_date >= {start}
                AND submission_date <= {end}
                ''')

            items = cursor.fetchall()
            sentence_lists = [items[i*10:(i+1)*10] for i in range(int(len(items)/10))]

            return sentence_lists

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