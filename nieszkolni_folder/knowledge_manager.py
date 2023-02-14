import os
import django
from django.db import connection

from nieszkolni_app.models import Pronunciation
from nieszkolni_app.models import Dictionary
from nieszkolni_app.models import Prompt
from nieszkolni_app.models import Question
from nieszkolni_app.models import Quiz
from nieszkolni_app.models import Assessment
from nieszkolni_app.models import Collection
from nieszkolni_app.models import Catalogue
from nieszkolni_app.models import Card
from nieszkolni_app.models import Book

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.vocabulary_manager import VocabularyManager
from nieszkolni_folder.cleaner import Cleaner

import random
import re

from nieszkolni_folder.clients_manager import ClientsManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class KnowledgeManager:
    def __init__(self):
        today_pattern = "%Y-%m-%d"

    def add_pronunciation(self, client, entry, coach):

        verify_client = ClientsManager().verify_client(client)
        if verify_client is False:
            return "The client does not exist!"

        entry = Cleaner().clean_quotation_marks(entry)

        check = self.check_if_pronunciation_deactivated(client, entry)
        if check:
            self.activate_pronunciation(client, entry, coach)
            return ("SUCCESS", "Entry reactivated")

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
                revision_days,
                status
                )
                VALUES (
                '{now_number}',
                '{today_number}',
                '{coach}',
                '{client}',
                '{entry}',
                '{today_number}',
                0,
                '',
                '',
                'active'
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
                AND status = 'active'
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
                WHERE status = 'active'
                ''')
            entries = cursor.fetchall()

            return entries

    def check_if_in_pronunciation(self, name, entry):
        entry = Cleaner().clean_quotation_marks(entry)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT entry
                FROM nieszkolni_app_pronunciation
                WHERE name = '{name}'
                AND entry = '{entry}'
                AND status = 'active'
                ''')

            result = cursor.fetchall()

            return result

    def check_if_pronunciation_deactivated(self, client, entry):
        entry = Pronunciation.objects.filter(
            name=client,
            entry=entry,
            status="inactive"
            )

        if entry.exists():
            return True
        else:
            return False

    def activate_pronunciation(self, client, entry, coach):
        entry = Pronunciation.objects.filter(
            name=client,
            entry=entry,
            status="inactive"
            ).first()

        entry.status = "active"
        entry.coach = coach
        entry.save()

    def deactivate_pronunciation(self, client):
        try:
            entries = Pronunciation.objects.filter(name=client)
            for entry in entries:
                entry.status = "inactive"
                entry.save()
            output = ("SUCCESS", f"All pronunciation entries of {client}'s removed")

        except Exception as e:
            output = ("ERROR", "Error")

        return output

    # Dictionary

    def upload_dictionary(self, english, polish, publicating_user, publication_date, deck):
        english = english.replace('"', "")
        english = english.replace("'", "’")

        polish = polish.replace('"', "")
        polish = polish.replace("'", "’")

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_dictionary (
                english,
                polish,
                publicating_user,
                publication_date,
                deck
                )
                VALUES (
                '{english}',
                '{polish}',
                '{publicating_user}',
                {publication_date},
                '{deck}')
                ON CONFLICT (english)
                DO UPDATE SET 
                english = '{english}',
                polish = '{polish}',
                publicating_user = '{publicating_user}',
                publication_date = {publication_date},
                deck = '{deck}'
                ''')

    def display_dictionary(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT english, polish, publicating_user, publication_date, deck
                FROM nieszkolni_app_dictionary
                ''')
            entries = cursor.fetchall()

            dictionary = []
            for entry in entries:
                dictionary_entry = {
                    "english": entry[0],
                    "polish": entry[1],
                    "publicating_user": entry[2],
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
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT polish
                FROM nieszkolni_app_dictionary
                WHERE english = '{english}'
                ''')
            polish = cursor.fetchone()

            if polish is None:
                return None
            else:
                polish = polish[0]
                return polish

    def add_to_book(self, name, english, publicating_user, deck):
        english = Cleaner().clean_quotation_marks(english)
        polish = self.translate(english)
        deck = deck
        today_number = TimeMachine().today_number()

        if polish is not None:
            add_entry = VocabularyManager().add_entry(
                name,
                deck,
                english,
                polish,
                publicating_user
                )

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
                    deck,
                    comment
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
                    '{deck}',
                    ''
                    ) ON CONFLICT
                    DO NOTHING
                    ''')

    def display_open_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                english,
                status,
                deck,
                publicating_user,
                name,
                comment,
                polish
                FROM nieszkolni_app_book
                WHERE deck = '{deck}'
                AND (status = 'open'
                OR status = 'rejected')
                ORDER BY english ASC
                LIMIT 1
                ''')

            entry = cursor.fetchone()

            if entry is not None:
                unique_id = entry[0]
                english = entry[1]
                polish = self.translate(english)
                publicating_user = entry[4]

                if polish is not None:
                    self.approve_book_entry(
                        unique_id,
                        english,
                        publicating_user
                        )

                    return None

                else:
                    return entry
            else:
                return None

    def count_open_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(DISTINCT english)
                FROM nieszkolni_app_book
                WHERE deck = '{deck}'
                AND (status = 'open'
                OR status = 'rejected')
                ''')

            entry = cursor.fetchone()
            if entry is not None:
                return entry[0]

            else:
                return 0

    def count_translated_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(DISTINCT english)
                FROM nieszkolni_app_book
                WHERE deck = '{deck}'
                AND status = 'translated'
                ''')

            entry = cursor.fetchone()
            if entry is not None:
                return entry[0]

            else:
                return 0

    def delete_book_entries_by_english(self, english):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_book
                WHERE english = '{english}'
                ''')

    def translate_book_entry(
            self,
            original_english,
            english,
            polish,
            current_user
            ):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET
                english = '{english}',
                polish = '{polish}',
                status = 'translated',
                translation_date = '{today_number}',
                translating_user = '{current_user}'
                WHERE english = '{original_english}'
                ''')

    def comment_on_book_entry(self, english, comment):
        comment = Cleaner().clean_quotation_marks(comment)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET comment = '{comment}'
                WHERE english = '{english}'
                ''')

    def approve_book_entry(self, unique_id, english, reviewing_user):
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET
                status = 'approved',
                revision_date = '{today_number}',
                reviewing_user = '{reviewing_user}'
                WHERE english = '{english}'
                ''')

            self.add_from_book_to_dictionary(english)

    def add_from_book_to_dictionary(self, english):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                polish,
                deck,
                name,
                publicating_user,
                publication_date
                FROM nieszkolni_app_book
                WHERE english = '{english}'
                ''')

            entries = cursor.fetchall()

            for entry in entries:
                unique_id = entry[0]
                polish = entry[1]
                publication_date = TimeMachine().today_number()
                deck = entry[2]
                client = entry[3]
                coach = entry[4]
                initiation_date = entry[5]

                check_if_in = self.translate(english)
                if check_if_in is None:
                    self.upload_dictionary(
                            english,
                            polish,
                            coach,
                            publication_date,
                            deck
                            )

                VocabularyManager().add_entry(
                    client,
                    deck,
                    english,
                    polish,
                    coach,
                    initiation_date
                    )

                with connection.cursor() as cursor:
                    cursor.execute(f'''
                        DELETE FROM nieszkolni_app_book
                        WHERE id = '{unique_id}'
                        ''')

    def display_translated_book(self, deck):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                english,
                polish,
                deck,
                publicating_user,
                name,
                comment
                FROM nieszkolni_app_book
                WHERE status = 'translated'
                AND deck = '{deck}'
                LIMIT 1
                ''')

            entry = cursor.fetchone()

            if entry is not None:
                name = entry[5]
                english = entry[1]
                polish = self.translate(english)
                publicating_user = entry[4]

                if polish is not None:
                    VocabularyManager().add_entry(
                        name,
                        deck,
                        english,
                        polish,
                        publicating_user
                        )

                    return None

                else:
                    return entry

            else:
                return None

    def reject_book_entry(self, english):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET status = 'rejected'
                WHERE english = '{english}'
                ''')

    def return_book_entry(self, current_user, english):
        entries = Book.objects.filter(english=english)
        entry = entries[0]
        coach = entry.publicating_user

        if coach != "automatic":
            for entry in entries:
                entry.status = "returned"
                entry.reviewing_user = current_user
                entry.save()

    def display_returned_book(self, current_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                english,
                status,
                deck,
                publicating_user,
                name,
                comment
                FROM nieszkolni_app_book
                WHERE status = 'returned'
                AND publicating_user = '{current_user}'
                ORDER BY english ASC
                LIMIT 1
                ''')

            entry = cursor.fetchone()

            return entry

    def correct_book_entry(self, english_old, english_new):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_book
                SET
                english = '{english_new}',
                status = 'open'
                WHERE english = '{english_old}'
                ''')

    def count_returned_book(self, current_user):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(id)
                FROM nieszkolni_app_book
                WHERE status = 'returned'
                AND publicating_user = '{current_user}'
                ORDER BY english ASC
                LIMIT 1
                ''')

            entry = cursor.fetchone()

            if entry is not None:
                entry = entry[0]
                return entry

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
                '{publication_date}',
                '{publicating_user}',
                '{entry}',
                '{entry_number}',
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

    def display_all_catalogues(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT catalogue_number, catalogue_name
                FROM nieszkolni_app_catalogue
                ORDER BY catalogue_name ASC
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
                ORDER BY prompt ASC
                ''')

            prompts = cursor.fetchall()

            return prompts

    def display_list_of_prompts(self, parent):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT prompt, parent, pattern
                FROM nieszkolni_app_prompt
                WHERE parent = '{parent}'
                ORDER BY prompt ASC
                ''')

            rows = cursor.fetchall()

            prompts = []
            for row in rows:
                prompts.append(row[0])

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

        verify_client = ClientsManager().verify_client(name)
        if verify_client is False:
            return "The client does not exist!"

        prompts = self.display_list_of_prompts("memories")
        if prompt not in prompts:
            return "The prompt does not exist!"

        left_option = Cleaner().clean_quotation_marks(left_option)
        right_option = Cleaner().clean_quotation_marks(right_option)

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
                '{publication_stamp}',
                '{publication_date}',
                '{coach}',
                '{name}',
                '{prompt}',
                '{left_option}',
                '{right_option}',
                '{due_date}',
                '{number_of_reviews}',
                '{answers}',
                '{revision_days}'
                )
                ON CONFLICT
                DO NOTHING
                ''')

    def check_if_in_memories(
            self,
            client,
            prompt,
            left_option,
            right_option=""
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT publication_stamp
                FROM nieszkolni_app_memory
                WHERE name = '{client}'
                AND prompt = '{prompt}'
                AND left_option = '{left_option}'
                AND right_option = '{right_option}'
                ''')

            data = cursor.fetchone()

            return False if data is None else True

    def display_all_memories(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT left_option
                FROM nieszkolni_app_memory
                ''')

            memories = cursor.fetchall()

            return memories

    def display_all_memories_entries(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                prompt,
                left_option,
                right_option
                FROM nieszkolni_app_memory
                ''')

            memories = cursor.fetchall()

            return memories

    def display_memories_by_client(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                prompt,
                left_option,
                right_option
                FROM nieszkolni_app_memory
                WHERE name = '{name}'
                ''')

            memories = cursor.fetchall()

            return memories

    def display_memory(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                prompt,
                left_option,
                right_option,
                name
                FROM nieszkolni_app_memory
                WHERE id = '{unique_id}'
                ''')

            memory = cursor.fetchone()

            return memory

    def remove_memory(self, unique_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_memory
                WHERE id = '{unique_id}'
                ''')

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
                AND nieszkolni_app_prompt.pattern != ''
                ''')

            memories = cursor.fetchall()

            parsed_memories = []
            for memory in memories:
                step_1 = memory[4].replace("left_option", memory[0])

                if memory[1] != "":
                    step_2 = step_1.replace("right_option", memory[1])
                    parsed_memories.append(step_2)

                else:
                    parsed_memories.append(step_1)

            return parsed_memories

    def add_catalogue_to_book(
            self,
            client,
            entry,
            current_user,
            deck
            ):

        try:
            entries = entry.split(": ")
            catalogue_number = entries[0]

            output = self.add_catalogue_to_book_by_no(
                client,
                catalogue_number,
                current_user,
                deck
                )

            return output

        except Exception as e:
            output = ("ERROR", "Catalogue could not be added")
            print(e)

            return output

    def add_catalogue_to_book_by_no(
            self,
            client,
            catalogue_number,
            current_user,
            deck
            ):

        check = Catalogue.objects.filter(catalogue_number=catalogue_number).exists()

        if check:

            phrases = self.display_list_of_phrases_in_catalogue(catalogue_number)

            cards = Card.objects.filter(
                    client=client,
                    deck=deck
                    )

            phrases_set = set(phrases)
            cards_set = set(card.english for card in cards)
            coverage_set = phrases_set.difference(cards_set)
            coverage = len(coverage_set) / len(phrases_set)
            coverage = round(1-coverage, 2)
            new_phrases = len(coverage_set)

            if coverage > 0.9:
                output = ("ERROR", "Catalogue has been added before")

                return output

            for phrase in phrases:
                add_phrase = self.add_to_book(
                    client,
                    phrase,
                    current_user,
                    deck
                    )

            output = ("SUCCESS", f"{new_phrases} new phrases added.")

        else:
            output = ("ERROR", "Catalogue does not exist")

        return output


