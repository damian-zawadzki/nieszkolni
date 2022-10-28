import os
import django
from django.db import connection
from nieszkolni_app.models import Pronunciation
from nieszkolni_app.models import Dictionary
from nieszkolni_app.models import Prompt
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.vocabulary_manager import VocabularyManager
from nieszkolni_folder.cleaner import Cleaner

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class KnowledgeManager:
    def __init__(self):
        today_pattern = "%Y-%m-%d"

    def add_pronunciation(self, name, entry, coach):
        now_number = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_pronunciation (
                publication_stamp,
                publication_date,
                coach,
                name,
                entry,
                due_date,
                number_of_reviews,
                answers,
                revision_days
                )
                VALUES (
                {now_number},
                {today_number},
                '{coach}',
                '{name}',
                '{entry}',
                {today_number},
                0,
                '',
                ''
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_pronunciation(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT entry
                FROM nieszkolni_app_pronunciation
                WHERE name = '{name}'
                ''')
            entries = cursor.fetchall()

            if entries is None:
                entries = ""
            else:
                entries = [entry[0] for entry in entries]

            return entries

    def display_all_pronunciation(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT entry
                FROM nieszkolni_app_pronunciation
                ''')
            entries = cursor.fetchall()

            return entries

    def check_if_in_pronunciation(self, name, entry):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT entry
                FROM nieszkolni_app_pronunciation
                WHERE name = '{name}'
                AND entry = '{entry}'
                ''')

            result = cursor.fetchall()

            return result

    def upload_dictionary(self, english, polish, user, publication_date, deck):
        english = english.replace('"', "")
        english = english.replace("'", "’")

        polish = polish.replace('"', "")
        polish = polish.replace("'", "’")

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_dictionary
                (english, polish, user, publication_date, deck)
                VALUES
                ('{english}', '{polish}', '{user}', {publication_date}, '{deck}')
                ON CONFLICT (english)
                DO UPDATE SET 
                english = '{english}',
                polish = '{polish}',
                user = '{user}',
                publication_date = {publication_date},
                deck = '{deck}'
                ''')

    def display_dictionary(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT english, polish, user, publication_date, deck
                FROM nieszkolni_app_dictionary
                ''')
            entries = cursor.fetchall()

            dictionary = []
            for entry in entries:
                dictionary_entry = {
                    "english": entry[0],
                    "polish": entry[1],
                    "user": entry[2],
                    "publication_date": entry[3],
                    "deck": entry[4]
                }

                dictionary.append(dictionary_entry)

        return dictionary

    def display_wordbook(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT english
                FROM nieszkolni_app_dictionary
                WHERE deck = 'vocabulary'
                OR deck != 'sentences'
                ''')
            wordbook = cursor.fetchall()

        return wordbook

    def display_sentencebook(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT english
                FROM nieszkolni_app_dictionary
                WHERE deck = 'sentences'
                ''')
            sentencebook = cursor.fetchall()

        return sentencebook

    def translate(self, english):
        print(english)
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT polish
                FROM nieszkolni_app_dictionary
                WHERE english = '{english}'
                ''')
            polish = cursor.fetchone()
            print(polish)
            if polish is None:
                return None
            else:
                polish = polish[0]
                return polish

    def add_to_book(self, name, english, publicating_user, deck):
        english = Cleaner().clean_quotation_marks(english)
        polish = self.translate(english)
        print(polish)
        deck = deck
        today_number = TimeMachine().today_number()

        if polish is not None:
            add_entry = VocabularyManager().add_entry(name, deck, english, polish, publicating_user)

        else:
            with connection.cursor() as cursor:
                cursor.execute(f'''
                    INSERT INTO nieszkolni_app_book (
                    name,
                    english,
                    polish,
                    publication_date,
                    publicating_user,
                    translation_date,
                    translating_user,
                    revision_date,
                    reviewing_user,
                    status,
                    deck
                    ) VALUES (
                    '{name}',
                    '{english}',
                    '',
                    {today_number},
                    '{publicating_user}',
                    0,
                    '',
                    0,
                    '',
                    'open',
                    '{deck}'
                    ) ON CONFLICT
                    DO NOTHING
                    ''')

    def display_open_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT id, english, status, deck
                FROM nieszkolni_app_book
                WHERE deck = '{deck}'
                AND (status = 'open'
                OR status = 'rejected')
                ''')
            entries = cursor.fetchall()
            if len(entries) == 0:
                return None
            else:
                return entries

    def delete_book_entry(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_book
                WHERE id = {unique_id}
                ''')

    def translate_book_entry(self, unique_id, polish):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET
                polish = '{polish}',
                status = 'translated'
                WHERE id = {unique_id}
                ''')

    def approve_book_entry(self, unique_id, user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET status = 'approved'
                WHERE id = {unique_id}
                ''')

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT english, polish, deck, name, publicating_user
                FROM nieszkolni_app_book
                WHERE id = {unique_id}
                ''')

            entry = cursor.fetchone()
            english = entry[0]
            polish = entry[1]
            publication_date = TimeMachine().today_number()
            deck = entry[2]
            client = entry[3]
            coach = entry[4]

            self.upload_dictionary(english, polish, user, publication_date, deck)
            VocabularyManager().add_entry(client, deck, english, polish, coach)

            with connection.cursor() as cursor:
                cursor.execute(f'''
                    DELETE FROM nieszkolni_app_book
                    WHERE id = {unique_id}
                    ''')

    def display_translated_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT id, english, polish, deck
                FROM nieszkolni_app_book
                WHERE status = 'translated'
                AND deck = '{deck}'
                ''')

            entries = cursor.fetchall()

            if len(entries) == 0:
                return None
            else:
                return entries

    def reject_book_entry(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET status = 'rejected'
                WHERE id = {unique_id}
                ''')

    def upload_catalogues(
            self,
            publication_date,
            publicating_user,
            entry,
            entry_number,
            catalogue_number,
            catalogue_name
            ):

        entry = Cleaner().clean_quotation_marks(entry)
        catalogue_name = Cleaner().clean_quotation_marks(catalogue_name)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_catalogue (
                publication_date,
                publicating_user,
                entry,
                entry_number,
                catalogue_number,
                catalogue_name
                )
                VALUES (
                {publication_date},
                '{publicating_user}',
                '{entry}',
                {entry_number},
                '{catalogue_number}',
                '{catalogue_name}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_catalogues(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT catalogue_name, catalogue_number
                FROM nieszkolni_app_catalogue
                ''')

            catalogues = cursor.fetchall()

            return catalogues

    def display_list_of_phrases_in_catalogue(self, catalogue_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT entry
                FROM nieszkolni_app_catalogue
                WHERE catalogue_number = {catalogue_number}
                ''')

            list_of_phrases = cursor.fetchall()

            phrases = [phrase[0] for phrase in list_of_phrases]

            return phrases

    def add_prompt(self, prompt, parent, pattern):
        pattern = Cleaner().clean_quotation_marks(pattern)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_prompt (
                prompt,
                parent,
                pattern
                ) VALUES (
                '{prompt}',
                '{parent}',
                '{pattern}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_prompts(self, parent):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT prompt, parent, pattern
                FROM nieszkolni_app_prompt
                WHERE parent = '{parent}'
                ''')

            prompts = cursor.fetchall()

            return prompts

    def display_all_prompts(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT prompt, parent, pattern
                FROM nieszkolni_app_prompt
                ''')

            prompts = cursor.fetchall()

            return prompts

    def check_if_in_prompts(self, prompt, parent):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT prompt
                FROM nieszkolni_app_prompt
                WHERE prompt = '{prompt}'
                AND parent = '{parent}'
                ''')

            prompts = cursor.fetchall()

            if len(prompts) == 0:
                return False
            else:
                return True

    def delete_prompt(self, prompt, parent):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_prompt
                WHERE prompt = '{prompt}'
                AND parent = '{parent}'
                ''')        

    def add_memory(
            self,
            coach,
            name,
            prompt,
            left_option,
            right_option=""
            ):

        publication_stamp = TimeMachine().now_number()
        publication_date = TimeMachine().today_number()
        due_date = TimeMachine().today_number()
        number_of_reviews = 0
        answers = ""
        revision_days = ""

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_memory (
                publication_stamp,
                publication_date,
                coach,
                name,
                prompt,
                left_option,
                right_option,
                due_date,
                number_of_reviews,
                answers,
                revision_days
                ) VALUES (
                {publication_stamp},
                {publication_date},
                '{coach}',
                '{name}',
                '{prompt}',
                '{left_option}',
                '{right_option}',
                {due_date},
                {number_of_reviews},
                '{answers}',
                '{revision_days}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def display_all_memories(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT left_option
                FROM nieszkolni_app_memory
                ''')

            memories = cursor.fetchall()

            return memories

    def display_memories(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                nieszkolni_app_memory.left_option,
                nieszkolni_app_memory.right_option,
                nieszkolni_app_memory.prompt,
                nieszkolni_app_prompt.prompt,
                nieszkolni_app_prompt.pattern,
                nieszkolni_app_memory.name
                FROM nieszkolni_app_memory
                INNER JOIN nieszkolni_app_prompt
                ON nieszkolni_app_memory.prompt = nieszkolni_app_prompt.prompt
                WHERE nieszkolni_app_memory.name = '{name}'
                ''')

            memories = cursor.fetchall()
            print(memories)

            parsed_memories = []
            for memory in memories:
                step_1 = memory[4].replace("left_option", memory[0])

                if memory[1] != "":
                    step_2 = step_1.replace("right_option", memory[1])
                    parsed_memories.append(step_2)

                else:
                    parsed_memories.append(step_1)

            return parsed_memories

