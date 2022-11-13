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
            component_id,
            course_id
            ):

        course_description = Cleaner().clean_quotation_marks(course_description)
        registration_description = Cleaner().clean_quotation_marks(registration_description)
        assessment_description = Cleaner().clean_quotation_marks(assessment_description)

        course_id = self.next_course_id()

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
            component_id
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
                component_id = '{component_id}'
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
                SELECT
                threshold
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
            status_type
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
                status_type
                )
                VALUES (
                'custom',
                {semester},
                '{course}',
                '{name}',
                {deadline_number},
                '{planning_user}',
                'ongoing',
                {item},
                '{status_type}'
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

    def display_current_courses(self, name):
        current_semester = 0
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT current_semester
                FROM nieszkolni_app_profile
                WHERE name = '{name}'
                ''')

            data = cursor.fetchone()
            current_semester = data[0]

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                course
                FROM nieszkolni_app_roadmap
                WHERE name = '{name}'
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
                SELECT name
                FROM nieszkolni_app_profile
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

    def add_grade(
            self,
            student,
            course,
            result,
            grade_type,
            examiner
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
                examiner
                )
                VALUES (
                {stamp},
                {today_number},
                '{student}',
                '{course}',
                {result},
                '{grade_type}',
                '{examiner}'
                )
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
                stamp
                FROM nieszkolni_app_grade
                WHERE student = '{student}'
                AND course = '{course}'
                ORDER BY stamp DESC
                ''')

            rows = cursor.fetchall()

            grades = []
            for row in rows:
                date = TimeMachine().number_to_system_date(row[0])
                grade = (date, row[1], row[2], row[3])
                grades.append(grade)

            return grades

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