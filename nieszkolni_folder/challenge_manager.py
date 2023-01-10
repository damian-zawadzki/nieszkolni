import os
import django
from django.db import connection

from nieszkolni_app.models import ChallengeMatrix

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.clients_manager import ClientsManager
from nieszkolni_folder.curriculum_planner import CurriculumPlanner
from nieszkolni_folder.curriculum_manager import CurriculumManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class ChallengeManager:
    def __init__(self):
        pass

    def add_challenge(
            self,
            matrix,
            step_type,
            step_number,
            title,
            text,
            image,
            module,
            activity_points
            ):

        title = Cleaner().clean_quotation_marks(title)
        text = Cleaner().clean_quotation_marks(text)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_challengematrix (
                matrix,
                step_type,
                step_number,
                title,
                text,
                image,
                module
                )
                VALUES (
                '{matrix}',
                '{step_type}',
                '{step_number}',
                '{title}',
                '{text}',
                '{image}',
                '{module}',
                '{activity_points}'
                )
                ''')

    def display_matrices(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT
                id,
                matrix
                FROM nieszkolni_app_challengematrix
                GROUP BY matrix
                ''')   

            matrices = cursor.fetchall()

            return matrices

    def display_matrix_by_id(self, matrix_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT matrix
                FROM nieszkolni_app_challengematrix
                WHERE id = '{matrix_id}'
                ''')   

            item = cursor.fetchone()

            if item is not None:
                matrix = item[0]
            else:
                matrix = None

            return matrix

    def display_challenges(self, matrix):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                matrix,
                step_type,
                step_number,
                title,
                text,
                image,
                module
                FROM nieszkolni_app_challengematrix
                WHERE matrix = '{matrix}'
                ''')   

            challenges = cursor.fetchall()

            return challenges

    def display_challenge(self, challenge_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                matrix,
                step_type,
                step_number,
                title,
                text,
                image,
                module
                FROM nieszkolni_app_challengematrix
                WHERE id = '{challenge_id}'
                ''')   

            challenge = cursor.fetchone()

            return challenge

    def update_challenge(
            self,
            matrix,
            step_type,
            step_number,
            title,
            text,
            image,
            module,
            challenge_id,
            activity_points
            ):

        title = Cleaner().clean_quotation_marks(title)
        text = Cleaner().clean_quotation_marks(text)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_challengematrix
                SET
                matrix = '{matrix}',
                step_type = '{step_type}',
                step_number = '{step_number}',
                title = '{title}',
                text = '{text}',
                image = '{image}',
                module = '{module}',
                activity_points = '{activity_points}'
                WHERE id = '{challenge_id}'
                ''')

    def display_next_process_number(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT process_number
                FROM nieszkolni_app_challenge
                ORDER BY process_number DESC
                LIMIT 1
                ''')

            last_process_number = cursor.fetchone()

            if last_process_number is None:
                next_process_number = 1000000
            else:
                next_process_number = int(last_process_number[0]) + 1

            return next_process_number

    def plan_challenges(self):
        clients = ClientsManager().list_current_clients()

        challenges_to_plan = []
        for client in clients:
            challenges = StreamManager().display_challenges(client)

            if len(challenges) != 0:
                challenges_to_plan.append((client, challenges))

        for challenge_to_plan in challenges_to_plan:
            matrix = challenge_to_plan[1][0]
            challenges = self.display_challenges(matrix)

            process_number = self.display_next_process_number()

            for challenge in challenges:

                stamp = TimeMachine().now_number()
                process_status = "uncompleted"
                process_completion_stamp = "0"
                step_type = challenge[2]
                step_id = challenge[0]
                step_number = challenge[3]

                if step_number == 1:
                    step_status = "unlocked"
                else:
                    step_status = "locked"

                step_completion_stamp = "0"
                client = challenge_to_plan[0]
                title = challenge[4]
                text = challenge[5]
                image = challenge[6]
                module = challenge[7]
                activity_points = 1

                if module == "not applicable":
                    item = 0
                else:
                    details = CurriculumManager().display_module(module)
                    deadline_number = TimeMachine().today_number() + 365
                    deadline = TimeMachine().number_to_system_date(deadline_number)

                    item = CurriculumPlanner().plan_curriculum(
                        deadline,
                        client,
                        module,
                        details[1],
                        details[2],
                        details[3],
                        "custom",
                        details[4],
                        details[5],
                        details[6]
                        )

                    CurriculumManager().change_to_invisible_uncompleted(
                        item,
                        "automatic"
                        )

                self.plan_challenge(
                    stamp,
                    matrix,
                    process_number,
                    process_status,
                    process_completion_stamp,
                    step_type,
                    step_id,
                    step_number,
                    step_status,
                    step_completion_stamp,
                    client,
                    title,
                    text,
                    image,
                    module,
                    item,
                    activity_points
                    )

            StreamManager().add_to_stream(
                client,
                "Covered challenge",
                matrix,
                "automatic"
                )

    def plan_challenge(
            self,
            stamp,
            matrix,
            process_number,
            process_status,
            process_completion_stamp,
            step_type,
            step_id,
            step_number,
            step_status,
            step_completion_stamp,
            client,
            title,
            text,
            image,
            module,
            item,
            activity_points
            ):

        title = Cleaner().clean_quotation_marks(title)
        text = Cleaner().clean_quotation_marks(text)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_challenge (
                stamp,
                matrix,
                process_number,
                process_status,
                process_completion_stamp,
                step_type,
                step_id,
                step_number,
                step_status,
                step_completion_stamp,
                client,
                title,
                text,
                image,
                module,
                item,
                activity_points
                )
                VALUES (
                '{stamp}',
                '{matrix}',
                '{process_number}',
                '{process_status}',
                '{process_completion_stamp}',
                '{step_type}',
                '{step_id}',
                '{step_number}',
                '{step_status}',
                '{step_completion_stamp}',
                '{client}',
                '{title}',
                '{text}',
                '{image}',
                '{module}',
                '{item}',
                '{activity_points}'
                )
                ''')

    def display_planned_challenges(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                matrix,
                process_number,
                process_status,
                process_completion_stamp,
                step_type,
                step_id,
                step_number,
                step_status,
                step_completion_stamp,
                client,
                title,
                text,
                image,
                module,
                item,
                activity_points
                FROM nieszkolni_app_challenge
                WHERE client = '{client}'
                AND process_status = 'uncompleted'
                AND process_status != 'removed'
                ''')

            rows = cursor.fetchall()

            if len(rows) != 0:
                process_number = rows[0][3]
                challenges = [row for row in rows if row[3] == process_number]

                return challenges

            else:
                return None

    def display_planned_challenge(self, challenge_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                matrix,
                process_number,
                process_status,
                process_completion_stamp,
                step_type,
                step_id,
                step_number,
                step_status,
                step_completion_stamp,
                client,
                title,
                text,
                image,
                module,
                item,
                activity_points
                FROM nieszkolni_app_challenge
                WHERE id = '{challenge_id}'
                AND process_status != 'removed'
                ''')

            challenge = cursor.fetchone()

            return challenge

    def display_processes(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                matrix,
                process_number,
                process_status,
                process_completion_stamp,
                step_type,
                step_id,
                step_number,
                step_status,
                step_completion_stamp,
                client,
                title,
                text,
                image,
                module,
                item,
                activity_points
                FROM nieszkolni_app_challenge
                WHERE process_status != 'removed'
                GROUP BY process_number
                ''')

            processes = cursor.fetchall()

            return processes

    def display_steps(self, process_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                stamp,
                matrix,
                process_number,
                process_status,
                process_completion_stamp,
                step_type,
                step_id,
                step_number,
                step_status,
                step_completion_stamp,
                client,
                title,
                text,
                image,
                module,
                item,
                activity_points
                FROM nieszkolni_app_challenge
                WHERE process_number = '{process_number}'
                ''')

            steps = cursor.fetchall()

            return steps

    def remove_process(self, process_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_challenge
                SET process_status = 'removed'
                WHERE process_number = '{process_number}'
                ''')

    def find_challenge(self, challenge):
        item = challenge[16]
        step_status = challenge[9]

        if step_status == "completed":
            call = False
            action = False
            value = "completed"
            cta = (call, action, value)

            return cta

        if item == 0:
            call = "Complete"
            action = "complete"
            value = ""
            cta = (call, action, value)

        else:
            assignment = CurriculumManager().display_assignment(item)
            status = assignment[11]

            if status == "completed":
                call = "Complete"
                action = "complete"
                value = ""
                cta = (call, action, value)

            else:
                action = "submit"
                cta = (assignment[17], action, assignment[19])

        return cta

    def check_if_process_completed(self, process_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT step_status
                FROM nieszkolni_app_challenge
                WHERE process_number = '{process_number}'
                ''')

            things = cursor.fetchall()

            statuses = [thing[0] for thing in things]

            if len(statuses) == 1 and statuses[0] == "completed":
                status = self.check_process_status(process_number)
                if status == "completed":
                    return True

                else:
                    self.complete_process(process_number)
                    return True

            else:
                return False

    def check_process_status(self, process_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT process_status
                FROM nieszkolni_app_challenge
                WHERE process_number = '{process_number}'
                ''')

            thing = cursor.fetchone()

            if thing is not None:
                status = thing[0]
            else:
                status = None

            return status

    def check_if_item_completed(self, challenge_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT item
                FROM nieszkolni_app_challenge
                WHERE id = '{challenge_id}'
                ''')

            item = cursor.fetchone()

            if item is not None:
                item = item[0]

                assignment = CurriculumManager().display_assignment(item)
                status = assignment[11]

                if status == "completed":
                    return True
                else:
                    return False
            else:
                return None

    def find_challenge_by_item(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT id
                FROM nieszkolni_app_challenge
                WHERE item = '{item}'
                ''')

            challenge_id = cursor.fetchone()

            if challenge_id is not None:
                return challenge_id[0]
            else:
                return None

    def complete_process(self, process_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_challenge
                SET process_status = 'completed'
                WHERE process_number = '{process_number}'
                ''')

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT client, matrix
                FROM nieszkolni_app_challenge
                WHERE process_number = '{process_number}'
                ''')

            info = cursor.fetchone()
            client = info[0]
            matrix = info[1]

            StreamManager().add_to_stream(
                client,
                "Completed challenge",
                matrix,
                "automatic"
                )

    def unlock_next_step(self, step_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_challenge
                SET step_status = 'unlocked'
                WHERE step_number = '{step_number}'
                ''')

    def check_step_status(self, process_number, step_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT step_status
                FROM nieszkolni_app_challenge
                WHERE process_number = '{process_number}'
                AND step_number = '{step_number}'
                ''')

            status = cursor.fetchone()

            if status is not None:
                status = status[0]

            return status

    def check_challenge_status(self, challenge_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT step_status
                FROM nieszkolni_app_challenge
                WHERE id = '{challenge_id}'
                ''')

            status = cursor.fetchone()

            if status is not None:
                status = status[0]

            return status

    def display_reward_by_item(self, item):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT activity_points
                FROM nieszkolni_app_challenge
                WHERE item = '{item}'
                ''')

            activity_points = cursor.fetchone()

            if activity_points is not None:
                activity_points = activity_points[0]

                return activity_points
            else:
                return None

    def assign_reward(self, challenge_id):
        check = self.check_challenge_status(challenge_id)

        if check != "completed":
            with connection.cursor() as cursor:
                cursor.execute(f'''
                    SELECT process_number, step_number, activity_points, client
                    FROM nieszkolni_app_challenge
                    WHERE id = '{challenge_id}'
                    ''')

                thing = cursor.fetchone()

                process_number = thing[0]
                step_number = thing[1]
                points = thing[2]
                client = thing[3]

                StreamManager().add_to_stream(
                    client,
                    "Activity",
                    f"challenge {process_number}{step_number};{points}",
                    "automatic"
                    )

    def complete_challenge(self, challenge_id):
        self.assign_reward(challenge_id)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_challenge
                SET step_status = 'completed'
                WHERE id = '{challenge_id}'
                RETURNING process_number, step_number
                ''')

            thing = cursor.fetchone()

            if thing is not None:
                process_number = thing[0]
                process_status = self.check_if_process_completed(process_number)

                if process_status is False:
                    step_number = thing[1]
                    next_step_number = step_number + 1
                    next_step_status = self.check_step_status(
                            process_number,
                            next_step_number
                            )

                    print(next_step_status)
                    if next_step_status == "locked":
                        self.unlock_next_step(next_step_number)

                return process_status

    def refresh_process(self, challenges):
        # problematic because it's looping through
        if challenges is not None:

            for challenge in challenges:
                challenge_id = challenge[0]
                process_number = challenge[3]
                item = challenge[16]

                if item != 0:
                    item_status = self.check_if_item_completed(challenge[0])

                    if item_status is True:
                        self.complete_challenge(challenge[0])

                process_status = self.check_if_process_completed(process_number)

            return process_status

        else:
            return True
