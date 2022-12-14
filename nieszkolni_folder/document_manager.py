import os
import django
import re
from django.db import connection
from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner
from nieszkolni_app.models import Material

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from docx.shared import Pt
from docx.shared import RGBColor

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class DocumentManager:
    def __init__(self):
        pass

    def create_assignment_doc(
            self,
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
            ):

        document = Document()

        # Label
        paragraph_0 = document.add_paragraph()

        paragraph_0 = document.add_heading()
        paragraph_format = paragraph_0.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph_format.alignment

        run = paragraph_0.add_run(
            f'''
            Written by: {name}
            Submitten on: {date}
            Reviewed by: {reviewing_user}
            Item: {item}
            Number of words: {wordcount}
            Errors: {major_errors}
            Punctuation and spelling errors: {minor_errors}
            Grade: {grade}
            ''')
        font = run.font
        font.name = "Times New Roman"
        font.size = Pt(12)
        font.bold = False
        font.color.rgb = RGBColor(0, 0, 0)

        # Heading
        paragraph_1 = document.add_heading()
        paragraph_format = paragraph_1.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph_format.alignment

        run = paragraph_1.add_run(title)
        font = run.font
        font.name = "Times New Roman"
        font.size = Pt(20)
        font.bold = True
        font.color.rgb = RGBColor(0, 0, 0)

        # Content
        paragraph_2 = document.add_paragraph()
        paragraph_format = paragraph_2.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph_format.alignment

        run = paragraph_2.add_run(flagged_content)
        font = run.font
        font.name = "Times New Roman"
        font.size = Pt(12)

        # Comment
        run = paragraph_2.add_run(comment)
        font = run.font
        font.name = "Times New Roman"
        font.size = Pt(12)

        file = document.save(f'nieszkolni_app/static/files/{item}.docx')

        return file

    def add_material(self, title, content):
        title = Cleaner().clean_quotation_marks(title)
        content = Cleaner().clean_quotation_marks(content)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO nieszkolni_app_material (
                title,
                content
                )
                VALUES (
                '{title}',
                '{content}'
                )
                ON CONFLICT (title)
                DO NOTHING
                ''')

    def display_materials(self):
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title
                FROM nieszkolni_app_material
                ''')

            materials = cursor.fetchall()

            return materials

    def display_material(self, title):
        title = Cleaner().clean_quotation_marks(title)

        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT
                title,
                content
                FROM nieszkolni_app_material
                WHERE title = '{title}'
                ''')

            material = cursor.fetchone()

            return material

    def delete_material(self, title):
        title = Cleaner().clean_quotation_marks(title[0])

        with connection.cursor() as cursor:
            cursor.execute(f'''
                DELETE FROM nieszkolni_app_material
                WHERE title = '{title}'
                ''')