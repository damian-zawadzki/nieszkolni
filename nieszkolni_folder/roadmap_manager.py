import os
import django

from django.db import connection

from nieszkolni_app.models import Roadmap
from nieszkolni_app.models import Course
from nieszkolni_app.models import Program
from nieszkolni_app.models import Grade
from nieszkolni_app.models import Profile
from nieszkolni_app.models import Spin

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

from nieszkolni_folder.curriculum_manager import CurriculumManager
from nieszkolni_folder.clients_manager import ClientsManager

import pandas as pd
import numpy as np

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class RoadmapManager:
    def __init__(self):
        pass

    def add_course(
            self,
            course,
            course_type,
            course_description,
            registration_description,
            assessment_description,
            assessment_method,
            link,
            reference_system,
            threshold,
            component_id
            ):

        course_description = Cleaner().clean_quotation_marks(course_description)
        registration_description = Cleaner().clean_quotation_marks(registration_description)
        assessment_description = Cleaner().clean_quotation_marks(assessment_description)

        course_id = self.display_next_course_id()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_course (
                course,
                course_type,
                course_description,
                registration_description,
                assessment_description,
                assessment_method,
                link,
                reference_system,
                threshold,
                component_id,
                course_id
                )
                VALUES (
                '{course}',
                '{course_type}',
                '{course_description}',
                '{registration_description}',
                '{assessment_description}',
                '{assessment_method}',
                '{link}',
                '{reference_system}',
                {threshold},
                '{component_id}',
                '{course_id}'
                )
                ''')

    def update_course(
            self,
            course,
            course_type,
            course_description,
            registration_description,
            assessment_description,
            assessment_method,
            link,
            reference_system,
            threshold,
            component_id,
            course_id
            ):

        course_description = Cleaner().clean_quotation_marks(course_description)
        registration_description = Cleaner().clean_quotation_marks(registration_description)
        assessment_description = Cleaner().clean_quotation_marks(assessment_description)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_course
                SET
                course = '{course}',
                course_type = '{course_type}',
                course_description = '{course_description}',
                registration_description = '{registration_description}',
                assessment_description = '{assessment_description}',
                assessment_method = '{assessment_method}',
                link = '{link}',
                reference_system = '{reference_system}',
                threshold = {threshold},
                component_id = '{component_id}',
                course_id = '{course_id}'
                WHERE course_id = '{course_id}'
                ''')

    def display_next_course_id(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT course_id
                FROM nieszkolni_app_course
                ORDER BY course_id DESC
                LIMIT 1
                ''')

            course_id = cursor.fetchone()

            if course_id is None:
                next_course_id = 1
            else:
                next_course_id = course_id[0] + 1

            return next_course_id

    def list_courses(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course,
                course_type,
                course_description,
                registration_description,
                assessment_description,
                assessment_method,
                link,
                reference_system,
                threshold,
                component_id
                FROM nieszkolni_app_course
                ''')

            courses = cursor.fetchall()

            return courses

    def display_course(self, course):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course,
                course_type,
                course_description,
                registration_description,
                assessment_description,
                assessment_method,
                link,
                reference_system,
                threshold,
                component_id,
                course_id
                FROM nieszkolni_app_course
                WHERE course = '{course}'
                ''')

            course = cursor.fetchone()

            return course

    def display_course_by_id(self, course_id):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course,
                course_type,
                course_description,
                registration_description,
                assessment_description,
                assessment_method,
                link,
                reference_system,
                threshold,
                component_id,
                course_id
                FROM nieszkolni_app_course
                WHERE course_id = '{course_id}'
                ''')

            course = cursor.fetchone()

            return course

    def display_courses(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course,
                course_type,
                course_description,
                registration_description,
                assessment_description,
                assessment_method,
                link,
                reference_system,
                threshold,
                component_id,
                course_id
                FROM nieszkolni_app_course
                ''')

            courses = cursor.fetchall()

            return courses

    def display_current_courses_by_client(self, client):

        current_semester = self.display_current_semester(client)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                r.program,
                r.course,
                r.status,
                c.course_id
                FROM nieszkolni_app_roadmap AS r
                LEFT JOIN nieszkolni_app_course AS c
                ON r.course = c.course
                WHERE r.name = '{client}'
                AND r.semester = '{current_semester}'
                ''')

            courses = cursor.fetchall()

            return courses

    def display_current_semester(self, client):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT current_semester
                FROM nieszkolni_app_profile
                WHERE name = '{client}'
                ''')

            current_semester = cursor.fetchone()

            if current_semester is not None:
                current_semester = current_semester[0]

            return current_semester

    def display_profile_names(self):
        clients = ClientsManager().list_current_clients()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_profile
                ''')

            profiles = cursor.fetchall()
            profiles = [profile[0] for profile in profiles]

        no_profile_clients = [
            client for client in clients
            if client not in profiles
            ]

        return no_profile_clients

    def display_courses_to_plan(self):

        matrices = CurriculumManager().display_matrices()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT course
                FROM nieszkolni_app_course
                ''')

            rows = cursor.fetchall()
            courses = [row[0] for row in rows]
            courses_to_plan = [matrix[0] for matrix in matrices if matrix[0] not in courses]

            return courses_to_plan

    def display_courses_by_ids(self, course_ids):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course,
                course_id
                FROM nieszkolni_app_course
                WHERE course_id IN {course_ids}
                ''')

            courses = cursor.fetchall()

            return courses

    def delete_course(self, course):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_course
                WHERE course = '{course}'
                ''')

    def display_course_threshold(self, course):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT threshold
                FROM nieszkolni_app_course
                WHERE course = '{course}'
                ''')

            data = cursor.fetchone()
            threshold = data[0]

            return threshold

    def add_roadmap(
            self,
            name,
            semester,
            course,
            deadline,
            planning_user,
            item,
            status_type,
            program
            ):

        deadline_number = TimeMachine().date_to_number(TimeMachine().american_to_system_date(deadline))

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_roadmap (
                roadmap_matrix,
                semester,
                course,
                name,
                deadline_number,
                planning_user,
                status,
                item,
                status_type,
                program
                )
                VALUES (
                '{course}',
                '{semester}',
                '{course}',
                '{name}',
                '{deadline_number}',
                '{planning_user}',
                'ongoing',
                '{item}',
                '{status_type}',
                '{program}'
                )
                ''')

    def update_roadmap_details(
            self,
            name,
            semester,
            course,
            deadline,
            planning_user,
            item,
            status,
            status_type,
            roadmap_id_number
            ):

        deadline_number = TimeMachine().date_to_number(TimeMachine().american_to_system_date(deadline))

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_roadmap
                SET
                roadmap_matrix = 'custom',
                semester = {semester},
                course = '{course}',
                name = '{name}',
                deadline_number = {deadline_number},
                planning_user = '{planning_user}',
                status = '{status}',
                status_type = '{status_type}',
                item = {item}
                WHERE roadmap_id_number = {roadmap_id_number}
                ''')

    def update_program_in_roadmap(
            self,
            name,
            semester,
            course,
            deadline,
            planning_user,
            item,
            status,
            status_type,
            roadmap_id_number
            ):

        deadline_number = TimeMachine().date_to_number(TimeMachine().american_to_system_date(deadline))

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_roadmap
                SET
                roadmap_matrix = 'custom',
                semester = {semester},
                course = '{course}',
                name = '{name}',
                deadline_number = {deadline_number},
                planning_user = '{planning_user}',
                status = '{status}',
                status_type = '{status_type}',
                item = {item}
                WHERE roadmap_id_number = {roadmap_id_number}
                ''')

    def display_roadmap(self, name, semester):
        semester = int(semester)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                roadmap_id_number,
                roadmap_matrix,
                course,
                name,
                deadline_number,
                planning_user,
                status
                FROM nieszkolni_app_roadmap
                WHERE name = '{name}'
                AND semester = {semester}
                ORDER BY status ASC
                ''')

            courses = cursor.fetchall()

            return courses

    def delete_roadmap_based_on_course(self, course):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_roadmap
                WHERE course = '{course}'
                ''')

    def display_roadmap_details(self, roadmap_id_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                roadmap_id_number,
                roadmap_matrix,
                course,
                name,
                deadline_number,
                planning_user,
                status,
                item,
                semester,
                status_type
                FROM nieszkolni_app_roadmap
                WHERE roadmap_id_number = {roadmap_id_number}
                ''')

            roadmap_details = cursor.fetchone()

            return roadmap_details

    def display_roadmaps(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT name
                FROM nieszkolni_app_roadmap
                WHERE semester = 1
                ''')

            stuff = cursor.fetchall()

            return stuff

    def display_current_courses(self, client):
        things = self.display_profiles()
        profiles = [thing[0] for thing in things]

        if client not in profiles:
            output = ("ERROR", "The client has no profile")

            return output

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT current_semester
                FROM nieszkolni_app_profile
                WHERE name = '{client}'
                ''')

            data = cursor.fetchone()
            current_semester = data[0]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT course
                FROM nieszkolni_app_roadmap
                WHERE name = '{client}'
                AND semester = '{current_semester}'
                ''')

            rows = cursor.fetchall()

            courses = []
            for row in rows:
                courses.append(row[0])

            return courses

    def update_roadmap(self, roadmap_id_number, status):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_roadmap
                SET status = '{status}'
                WHERE roadmap_id_number = {roadmap_id_number}
                ''')

    def remove_roadmap(self, roadmap_id_number):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_roadmap
                WHERE roadmap_id_number = {roadmap_id_number}
                ''')

    def add_profile(
            self,
            name,
            display_name,
            avatar,
            current_english_level,
            current_semester,
            current_specialization,
            current_degree,
            early_admission,
            semester_1_status,
            semester_2_status,
            semester_3_status,
            semester_4_status,
            semester_5_status,
            semester_6_status,
            semester_7_status,
            semester_8_status,
            semester_9_status,
            semester_10_status,
            semester_11_status,
            semester_12_status,
            semester_13_status,
            semester_14_status,
            semester_15_status,
            semester_16_status,
            associates_degree_status,
            bachelors_degree_status,
            masters_degree_status,
            doctorate_degree_status,
            professors_title_status
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_profile (
                name,
                display_name,
                avatar,
                current_english_level,
                current_semester,
                current_specialization,
                current_degree,
                early_admission,
                semester_1_status,
                semester_2_status,
                semester_3_status,
                semester_4_status,
                semester_5_status,
                semester_6_status,
                semester_7_status,
                semester_8_status,
                semester_9_status,
                semester_10_status,
                semester_11_status,
                semester_12_status,
                semester_13_status,
                semester_14_status,
                semester_15_status,
                semester_16_status,
                associates_degree_status,
                bachelors_degree_status,
                masters_degree_status,
                doctorate_degree_status,
                professors_title_status
                )
                VALUES (
                '{name}',
                '{display_name}',
                '{avatar}',
                '{current_english_level}',
                {current_semester},
                '{current_specialization}',
                '{current_degree}',
                '{early_admission}',
                '{semester_1_status}',
                '{semester_2_status}',
                '{semester_3_status}',
                '{semester_4_status}',
                '{semester_5_status}',
                '{semester_6_status}',
                '{semester_7_status}',
                '{semester_8_status}',
                '{semester_9_status}',
                '{semester_10_status}',
                '{semester_11_status}',
                '{semester_12_status}',
                '{semester_13_status}',
                '{semester_14_status}',
                '{semester_15_status}',
                '{semester_16_status}',
                '{associates_degree_status}',
                '{bachelors_degree_status}',
                '{masters_degree_status}',
                '{doctorate_degree_status}',
                '{professors_title_status}'
                )
                ON CONFLICT (name)
                DO NOTHING
                ''')

    def update_profile(
            self,
            name,
            display_name,
            avatar,
            current_english_level,
            current_semester,
            current_specialization,
            current_degree,
            early_admission,
            semester_1_status,
            semester_2_status,
            semester_3_status,
            semester_4_status,
            semester_5_status,
            semester_6_status,
            semester_7_status,
            semester_8_status,
            semester_9_status,
            semester_10_status,
            semester_11_status,
            semester_12_status,
            semester_13_status,
            semester_14_status,
            semester_15_status,
            semester_16_status,
            associates_degree_status,
            bachelors_degree_status,
            masters_degree_status,
            doctorate_degree_status,
            professors_title_status
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_profile
                SET
                display_name = '{display_name}',
                avatar = '{avatar}',
                current_english_level = '{current_english_level}',
                current_semester = {current_semester},
                current_specialization = '{current_specialization}',
                current_degree = '{current_degree}',
                early_admission = '{early_admission}',
                semester_1_status = '{semester_1_status}',
                semester_2_status = '{semester_2_status}',
                semester_3_status = '{semester_3_status}',
                semester_4_status = '{semester_4_status}',
                semester_5_status = '{semester_5_status}',
                semester_6_status = '{semester_6_status}',
                semester_7_status = '{semester_7_status}',
                semester_8_status = '{semester_8_status}',
                semester_9_status = '{semester_9_status}',
                semester_10_status = '{semester_10_status}',
                semester_11_status = '{semester_11_status}',
                semester_12_status = '{semester_12_status}',
                semester_13_status = '{semester_13_status}',
                semester_14_status = '{semester_14_status}',
                semester_15_status = '{semester_15_status}',
                semester_16_status = '{semester_16_status}',
                associates_degree_status = '{associates_degree_status}',
                bachelors_degree_status = '{bachelors_degree_status}',
                masters_degree_status = '{masters_degree_status}',
                doctorate_degree_status = '{doctorate_degree_status}',
                professors_title_status = '{professors_title_status}'
                WHERE name = '{name}'
                ''')

    def display_profiles(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                display_name,
                avatar,
                current_english_level,
                current_semester,
                current_specialization,
                current_degree,
                early_admission,
                semester_1_status,
                semester_2_status,
                semester_3_status,
                semester_4_status,
                semester_5_status,
                semester_6_status,
                semester_7_status,
                semester_8_status,
                semester_9_status,
                semester_10_status,
                semester_11_status,
                semester_12_status,
                semester_13_status,
                semester_14_status,
                semester_15_status,
                semester_16_status,
                associates_degree_status,
                bachelors_degree_status,
                masters_degree_status,
                doctorate_degree_status,
                professors_title_status
                FROM nieszkolni_app_profile
                ORDER BY name ASC
                ''')

            profiles = cursor.fetchall()

            return profiles

    def display_profile(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                name,
                display_name,
                avatar,
                current_english_level,
                current_semester,
                current_specialization,
                current_degree,
                early_admission,
                semester_1_status,
                semester_2_status,
                semester_3_status,
                semester_4_status,
                semester_5_status,
                semester_6_status,
                semester_7_status,
                semester_8_status,
                semester_9_status,
                semester_10_status,
                semester_11_status,
                semester_12_status,
                semester_13_status,
                semester_14_status,
                semester_15_status,
                semester_16_status,
                associates_degree_status,
                bachelors_degree_status,
                masters_degree_status,
                doctorate_degree_status,
                professors_title_status
                FROM nieszkolni_app_profile
                WHERE name = '{name}'
                ''')

            profile = cursor.fetchone()

            return profile

    def display_semesters(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                semester_1_status,
                semester_2_status,
                semester_3_status,
                semester_4_status,
                semester_5_status,
                semester_6_status,
                semester_7_status,
                semester_8_status,
                semester_9_status,
                semester_10_status,
                semester_11_status,
                semester_12_status,
                semester_13_status,
                semester_14_status,
                semester_15_status,
                semester_16_status
                FROM nieszkolni_app_profile
                WHERE name = '{name}'
                ''')

            rows = cursor.fetchone()

            if rows is None:
                semesters = []
            else:
                semesters = list(rows)

            return semesters

    def display_degrees(self, name):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                associates_degree_status,
                bachelors_degree_status,
                masters_degree_status,
                doctorate_degree_status,
                professors_title_status
                FROM nieszkolni_app_profile
                WHERE name = '{name}'
                ''')

            data = cursor.fetchone()

            if data is None:
                degrees = dict()
            else:
                degrees = dict()
                degrees.update({"associate": data[0]})
                degrees.update({"bachelor": data[1]})
                degrees.update({"master": data[2]})
                degrees.update({"doctorate": data[3]})
                degrees.update({"professor": data[4]})

            return degrees

    # Grades

    def add_grade(
            self,
            student,
            course,
            result,
            grade_type,
            examiner,
            test
            ):

        stamp = TimeMachine().now_number()
        today_number = TimeMachine().today_number()

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_grade (
                stamp,
                date_number,
                student,
                course,
                result,
                grade_type,
                examiner,
                test
                )
                VALUES (
                '{stamp}',
                '{today_number}',
                '{student}',
                '{course}',
                '{result}',
                '{grade_type}',
                '{examiner}',
                '{test}'
                )
                ''')

    def remove_grade(self, grade_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_grade
                WHERE id = '{grade_id}'
                ''')

    def display_grades(
            self,
            student,
            course
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                date_number,
                result,
                grade_type,
                examiner,
                course,
                stamp,
                id,
                test
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                ORDER BY stamp DESC
                ''')

            rows = cursor.fetchall()

            grades = []
            for row in rows:
                date = TimeMachine().number_to_system_date(row[0])
                grade = (date, row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                grades.append(grade)

            return grades

    def display_grade(self, grade_id):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                date_number,
                result,
                grade_type,
                examiner,
                course,
                stamp,
                id,
                test
                FROM nieszkolni_app_grade
                WHERE id = '{grade_id}'
                ''')

            grade = cursor.fetchone()

            date = TimeMachine().number_to_system_date(grade[0])
            grade = (
                    date,
                    grade[1],
                    grade[2],
                    grade[3],
                    grade[4],
                    grade[5],
                    grade[6]
                    )

            return grade

    def display_current_grades_by_client(self, client):
        courses = self.display_current_courses(client)

        all_grades = []
        for course in courses:
            grades = self.display_grades(client, course)
            all_grades.extend(grades)

        return all_grades

    def display_current_results_by_client(self, client):
        grades = self.display_current_grades_by_client(client)
        midterm_grades = [grade for grade in grades if grade[2] == "midterm"]
        final_grades = [grade for grade in grades if grade[2] == "final"]

        date_m = [grade[0] for grade in midterm_grades]
        grade_m = [grade[1] for grade in midterm_grades]
        grade_type_m = [grade[2] for grade in midterm_grades]
        course_m = [grade[4] for grade in midterm_grades]

        stamp_f = [grade[5] for grade in final_grades]
        date_f = [grade[0] for grade in final_grades]
        grade_f = [grade[1] for grade in final_grades]
        course_f = [grade[4] for grade in final_grades]

        midterms = ({
                "date": date_m,
                "grade": grade_m,
                "course": course_m
                })

        table_m = pd.DataFrame(midterms, columns=[
                "date",
                "grade",
                "course"
                ])

        table_m_2 = table_m.groupby(["course"]).mean(numeric_only=True).reset_index()

        midterm_results = list(table_m_2.itertuples(
                index=False,
                name=None
                ))

        finals = ({
                "stamp": stamp_f,
                "date": date_f,
                "grade": grade_f,
                "course": course_f
                })

        table_f = pd.DataFrame(finals, columns=[
                "stamp",
                "date",
                "grade",
                "course"
                ])

        table_f_2 = table_f.drop_duplicates()
        table_f_3 = table_f_2.groupby(["course"])["stamp"].max().reset_index()
        # table_f_3["grade"] = np.nan
        table_f_4 = table_f_2.groupby(["course", "stamp"])["grade"].max().reset_index()
        table_f_5 = table_f_3.merge(
                table_f_4,
                on="stamp",
                how="left",
                suffixes=("", "_y")
                )

        final_results = list(table_f_5[["course", "grade"]].itertuples(
                index=False,
                name=None
                ))

        midterm_results = [
            result for result in midterm_results
            if result[0] not in course_f
            ]

        final_results.extend(midterm_results)

        results = [(result[0], round(result[1])) for result in final_results]

        return results

    def display_last_final_grade(
            self,
            student,
            course
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                result
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                AND grade_type = 'final'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                result = -1
            else:
                result = data[1]

            return result

    def display_average_final_grade(
            self,
            student,
            course
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT AVG (result)
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                AND grade_type = 'final'
                ''')

            data = cursor.fetchone()

            if data is None:
                result = -1
            else:
                result = data[0]

            return result

    def display_last_midterm_grade(
            self,
            student,
            course
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                stamp,
                result
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                AND grade_type = 'midterm'
                ORDER BY stamp DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                result = -1
            else:
                result = data[1]

            return result

    def display_average_midterm_grade(
            self,
            student,
            course
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT AVG(result)
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                AND grade_type = 'midterm'
                ''')

            data = cursor.fetchone()

            if data is None:
                result = -1
            else:
                result = data[0]

            return result

    def display_next_story_number(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT story
                FROM nieszkolni_app_spin
                ORDER BY story DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                next_story_number = 1
            else:
                next_story_number = data[0] + 1

            return next_story_number

    def display_story_numbers(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT DISTINCT story
                FROM nieszkolni_app_spin
                ORDER BY story ASC
                ''')

            rows = cursor.fetchall()

            if rows is None:
                story_numbers = []
            else:
                story_numbers = [row[0] for row in rows]

            return story_numbers

    def display_scene_numbers(self, story):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT scene
                FROM nieszkolni_app_spin
                WHERE story = '{story}'
                ''')

            scene_numbers = cursor.fetchall()

            return scene_numbers

    def display_next_scene_number(self, story):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT scene
                FROM nieszkolni_app_spin
                ORDER BY scene DESC
                LIMIT 1
                ''')

            data = cursor.fetchone()

            if data is None:
                next_scene_number = 1
            else:
                next_scene_number = data[0] + 1

            return next_scene_number

    def add_spin(
            self,
            scene,
            message,
            option_a_text,
            option_b_text,
            option_c_text,
            option_d_text,
            option_a_view,
            option_b_view,
            option_c_view,
            option_d_view,
            option_key,
            option_a_value,
            option_b_value,
            option_c_value,
            option_d_value,
            view_type,
            story
            ):

        message = Cleaner().clean_quotation_marks(message)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_spin (
                scene,
                message,
                option_a_text,
                option_b_text,
                option_c_text,
                option_d_text,
                option_a_view,
                option_b_view,
                option_c_view,
                option_d_view,
                option_key,
                option_a_value,
                option_b_value,
                option_c_value,
                option_d_value,
                view_type,
                story
                )
                VALUES (
                '{scene}',
                '{message}',
                '{option_a_text}',
                '{option_b_text}',
                '{option_c_text}',
                '{option_d_text}',
                '{option_a_view}',
                '{option_b_view}',
                '{option_c_view}',
                '{option_d_view}',
                '{option_key}',
                '{option_a_value}',
                '{option_b_value}',
                '{option_c_value}',
                '{option_d_value}',
                '{view_type}',
                '{story}'
                )
                ON CONFLICT (scene)
                DO NOTHING
                ''')

    def display_story(self, story):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                scene,
                message,
                option_a_text,
                option_b_text,
                option_c_text,
                option_d_text,
                option_a_view,
                option_b_view,
                option_c_view,
                option_d_view,
                option_key,
                option_a_value,
                option_b_value,
                option_c_value,
                option_d_value,
                view_type,
                story
                FROM nieszkolni_app_spin
                WHERE story = '{story}'
                ''')

            items = cursor.fetchall()

            return items

    def display_next_scene(self, story, scene):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                message,
                option_a_text,
                option_b_text,
                option_c_text,
                option_d_text,
                option_a_view,
                option_b_view,
                option_c_view,
                option_d_view,
                option_key,
                option_a_value,
                option_b_value,
                option_c_value,
                option_d_value,
                view_type,
                story
                FROM nieszkolni_app_spin
                WHERE story = '{story}'
                AND scene = '{scene}'
                ''')

            item = cursor.fetchone()

            return item

    def display_scene(self, scene):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                message,
                option_a_text,
                option_b_text,
                option_c_text,
                option_d_text,
                option_a_view,
                option_b_view,
                option_c_view,
                option_d_view,
                option_key,
                option_a_value,
                option_b_value,
                option_c_value,
                option_d_value,
                view_type,
                story
                FROM nieszkolni_app_spin
                WHERE scene = '{scene}'
                ''')

            item = cursor.fetchone()

            return item

    def update_spin(
            self,
            scene,
            message,
            option_a_text,
            option_b_text,
            option_c_text,
            option_d_text,
            option_a_view,
            option_b_view,
            option_c_view,
            option_d_view,
            option_key,
            option_a_value,
            option_b_value,
            option_c_value,
            option_d_value,
            view_type,
            story
            ):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_spin
                SET
                message = '{message}',
                option_a_text = '{option_a_text}',
                option_b_text = '{option_b_text}',
                option_c_text = '{option_c_text}',
                option_d_text = '{option_d_text}',
                option_a_view = '{option_a_view}',
                option_b_view = '{option_b_view}',
                option_c_view = '{option_c_view}',
                option_d_view = '{option_d_view}',
                option_key = '{option_key}',
                option_a_value = '{option_a_value}',
                option_b_value = '{option_b_value}',
                option_c_value = '{option_c_value}',
                option_d_value = '{option_d_value}',
                view_type = '{view_type}',
                story = '{story}'
                WHERE scene = '{scene}'
                ''')

    def add_program(
            self,
            program_name,
            degree,
            description,
            courses,
            image
            ):

        description = Cleaner().clean_quotation_marks(description)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_program (
                program_name,
                degree,
                description,
                courses,
                image
                )
                VALUES (
                '{program_name}',
                '{degree}',
                '{description}',
                '{courses}',
                '{image}'
                )
                ''')

    def update_program(
            self,
            program_name,
            degree,
            description,
            courses,
            image,
            program_id
            ):

        description = Cleaner().clean_quotation_marks(description)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE nieszkolni_app_program
                SET
                program_name = '{program_name}',
                degree = '{degree}',
                description = '{description}',
                courses = '{courses}',
                image = '{image}'
                WHERE id = '{program_id}'
                ''')

    def display_programs(self):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                id,
                program_name,
                degree
                FROM nieszkolni_app_program
                ''')

            programs = cursor.fetchall()

            return programs

    def display_program(self, program_id):

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                program_name,
                degree,
                description,
                courses,
                image
                FROM nieszkolni_app_program
                WHERE id = '{program_id}'
                ''')

            program = cursor.fetchone()

            return program