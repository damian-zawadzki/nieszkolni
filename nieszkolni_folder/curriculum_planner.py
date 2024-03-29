import os
import django

from django.db import connection

from nieszkolni_app.models import Curriculum
from nieszkolni_app.models import Module
from nieszkolni_app.models import Matrix
from nieszkolni_app.models import Library
from nieszkolni_app.models import Roadmap
from nieszkolni_app.models import Profile

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.sentence_manager import SentenceManager
from nieszkolni_folder.quiz_manager import QuizManager
from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.vocabulary_manager import VocabularyManager
from nieszkolni_folder.back_office_manager import BackOfficeManager
from nieszkolni_folder.roadmap_manager import RoadmapManager
from nieszkolni_folder.clients_manager import ClientsManager
from nieszkolni_folder.stream_manager import StreamManager

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class CurriculumPlanner:
    def __init__(self):
        pass

    def plan_curriculum(
            self,
            deadline,
            client,
            component_id,
            assignment_type,
            title,
            content,
            matrix,
            resources,
            conditions,
            reference
            ):

        item = CurriculumManager().next_item()
        component_type = assignment_type

        CurriculumManager().add_curriculum(
            item,
            deadline,
            client,
            component_id,
            component_type,
            assignment_type,
            title,
            content,
            matrix,
            resources,
            conditions,
            reference
            )

        if assignment_type == "sentences" or assignment_type == "translation":
            set_details = SentenceManager().display_set(reference)
            set_id = set_details[0]
            sentence_ids = set_details[2]

            SentenceManager().compose_sentence_lists(
                client,
                item,
                set_id,
                sentence_ids,
                )

        elif assignment_type == "quiz":
            QuizManager().plan_quiz(client, item, reference)

        return item

    def plan_curricula(
            self,
            client,
            matrix,
            starting_date_number
            ):

        modules = CurriculumManager().display_matrix(matrix)

        for module in modules:
            component_id = module["component_id"]
            limit_number = module["limit_number"]

            entry = CurriculumManager().display_module(component_id)

            assignment_type = entry[1]
            title = entry[2]
            content = entry[3]
            resources = entry[4]
            conditions = entry[5]
            reference = entry[6]

            deadline_number = int(starting_date_number) + limit_number
            deadline = TimeMachine().number_to_system_date(deadline_number)

            self.plan_curriculum(
                deadline,
                client,
                component_id,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                conditions,
                reference
                )

    def plan_multiple_curricula(
            self,
            deadline,
            clients,
            component_id,
            assignment_type,
            title,
            content,
            matrix,
            resources,
            conditions,
            reference
            ):

        for client in clients:
            self.plan_curriculum(
                deadline,
                client,
                component_id,
                assignment_type,
                title,
                content,
                matrix,
                resources,
                conditions,
                reference
                )

    def plan_program(
            self,
            client,
            current_user,
            program_id,
            semester
            ):

        program = RoadmapManager().display_program(program_id)

        rows = StreamManager().find_by_command_and_client(
            "Program",
            client
            )

        check_if_planned = False
        if rows is not None:
            for row in rows:
                entry = row[5].split(";")
                if entry[0] == semester and entry[1] == program[0]:
                    check_if_planned = True

        if check_if_planned is True:
            return "The client has such a program already!"
        else:
            if program[3].count(", ") > 0:
                course_ids_list = program[3].split(", ")
            else:
                course_ids_list = []
                course_ids_list.append(program[3])

            self.plan_courses(
                    client,
                    current_user,
                    course_ids_list,
                    semester,
                    program[0]
                    )

            StreamManager().add_to_stream(
                client,
                "Program",
                f"{semester};{program[0]}",
                current_user
                )

            return "Program assigned!"

    def plan_courses(
            self,
            client,
            current_user,
            course_ids_list,
            semester,
            program
            ):

        outputs = []

        if len(course_ids_list) > 1:
            course_ids = tuple(course_ids_list)
        else:
            course_ids = f"({course_ids_list[0]})"

        courses = RoadmapManager().display_courses_by_ids(course_ids)
        deadline_roadmap = BackOfficeManager().display_end_of_semester()
        starting_date_number = TimeMachine().academic_week_start_number()

        check_courses = len(courses) == 0
        if check_courses:
            output = ("ERROR", "No such product exists")
            outputs.append(output)
            return outputs

        for course in courses:
            matrix = course[0]

            check_registration = Roadmap.objects.filter(
                semester=semester,
                course=matrix,
                name=client
                ).exists()

            if check_registration:
                output_client = ("ERROR", "You're already registered for this course")
                output_staff = ("ERROR", "Client is already registered for this course")
                if client != current_user:
                    outputs.append(output_staff)
                else:
                    outputs.append(output_client)
            else:
                RoadmapManager().add_roadmap(
                    client,
                    semester,
                    matrix,
                    deadline_roadmap,
                    current_user,
                    -1,
                    "automatic",
                    program
                    )

                self.plan_curricula(
                    client,
                    matrix,
                    starting_date_number
                    )

                output_client = ("SUCCESS", "You've successfully registered for this course")
                output_staff = ("SUCCESS", "Client registered for the course")
                if client != current_user:
                    outputs.append(output_staff)
                else:
                    outputs.append(output_client)

        return outputs

    def plan_courses_now(
            self,
            client,
            current_user,
            course_ids_list
            ):

        profile = Profile.objects.get(name=client)
        semester = profile.current_semester
        program = profile.current_program

        outputs = self.plan_courses(
            client,
            current_user,
            course_ids_list,
            semester,
            program
            )

        return outputs

    def client_to_plan_program(self):
        start = BackOfficeManager().display_start_of_semester()
        end = BackOfficeManager().display_end_of_semester()
        start_number = TimeMachine().date_to_number(start)
        end_number = TimeMachine().date_to_number(end)
        rows = StreamManager().find_by_command("Program")
        covered_clients = set()

        if rows is not None:
            for row in rows:
                if row[1] >= start_number - 21 and row[1] < end_number:
                    covered_clients.add(row[3])

        clients = ClientsManager().list_current_clients()
        clients = set(clients)
        clients.difference_update(covered_clients)

        return clients

    def remove_multiple_curricula(
            self,
            clients,
            component_id,
            deadline
            ):

        deadline = TimeMachine().date_to_number(deadline)

        for client in clients:
            CurriculumManager().remove_curricula(
                client,
                component_id,
                deadline
                )

    def display_expiration_dates(self, clients):

        dates = []

        for client in clients:

            date = CurriculumManager().display_expiration_date(
                client
                )

            dates.append(date)

        dates.sort(key=lambda date: (date[1], date[0]))
        expired = [date for date in dates if date[1] == "expired"]
        valid = [date for date in dates if date[1] != "expired"]
        results = expired + valid

        return results

    def assign_course(
            self,
            client,
            current_user,
            course,
            semester,
            program
            ):

        check = Roadmap.objects.filter(
            name=client,
            course=course,
            semester=semester
            ).exists()

        if check is True:
            output = ("ERROR", "Course already assigned")
            return output

        deadline_roadmap = BackOfficeManager().display_end_of_semester()
        roadmaps = Roadmap.objects.filter(
                name=client,
                semester=semester
                )
        program = roadmaps[0].program

        RoadmapManager().add_roadmap(
            client,
            semester,
            course,
            deadline_roadmap,
            current_user,
            -1,
            "automatic",
            program
            )

        output = ("SUCCESS", "Course assigned")

        return output

    def assign_program(
            self,
            client,
            program,
            semester
            ):

        roadmaps = Roadmap.objects.filter(
                name=client,
                semester=semester
                )

        for roadmap in roadmaps:
            roadmap.program = program
            roadmap.save()
