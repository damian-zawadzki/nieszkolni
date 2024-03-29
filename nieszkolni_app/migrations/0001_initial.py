# Generated by Django 4.0.4 on 2022-11-13 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('quiz_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('client', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('card_id', models.IntegerField(primary_key=True, serialize=False)),
                ('client', models.CharField(max_length=200)),
                ('deck', models.CharField(max_length=200)),
                ('english', models.CharField(max_length=200)),
                ('polish', models.CharField(max_length=200)),
                ('publication_date', models.IntegerField()),
                ('due_date', models.IntegerField()),
                ('interval', models.IntegerField()),
                ('number_of_reviews', models.IntegerField()),
                ('answers', models.TextField(default='')),
                ('card_opening_times', models.TextField(default='')),
                ('card_closing_times', models.TextField(default='')),
                ('durations', models.TextField(default='')),
                ('card_revision_days', models.TextField(default='')),
                ('line', models.IntegerField()),
                ('coach', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Catalogue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publication_date', models.IntegerField()),
                ('publicating_user', models.CharField(default='', max_length=200)),
                ('entry', models.CharField(default='', max_length=200)),
                ('entry_number', models.IntegerField()),
                ('catalogue_number', models.IntegerField()),
                ('catalogue_name', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('user_type', models.CharField(default='client', max_length=200)),
                ('name', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('phone_number', models.IntegerField(default=987654321)),
                ('contact_email_address', models.CharField(default='', max_length=200)),
                ('school', models.CharField(default='-', max_length=200)),
                ('internal_email_address', models.CharField(default='', max_length=200)),
                ('meeting_duration', models.IntegerField(default=55)),
                ('price', models.IntegerField(default=0)),
                ('acquisition_channel', models.CharField(default='', max_length=200)),
                ('recommenders', models.CharField(default='', max_length=200)),
                ('reasons_for_resignation', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
                ('coach', models.CharField(default='', max_length=200)),
                ('level', models.CharField(default='', max_length=200)),
                ('daily_limit_of_new_cards', models.IntegerField(default=25, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_name', models.CharField(default='', max_length=200)),
                ('collection_id', models.IntegerField(default=0)),
                ('question_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('list_number', models.IntegerField()),
                ('sentence_number', models.IntegerField(primary_key=True, serialize=False)),
                ('sentence_id', models.IntegerField()),
                ('name', models.CharField(default='', max_length=200)),
                ('polish', models.TextField(default='')),
                ('english', models.TextField(default='')),
                ('glossary', models.TextField(default='')),
                ('submission_stamp', models.IntegerField()),
                ('submission_date', models.IntegerField()),
                ('status', models.CharField(default='', max_length=200)),
                ('translation', models.TextField(default='')),
                ('result', models.CharField(default='', max_length=200)),
                ('reviewing_user', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course', models.CharField(max_length=200)),
                ('course_type', models.CharField(default='', max_length=200)),
                ('course_description', models.TextField(default='')),
                ('registration_description', models.TextField(default='')),
                ('assessment_description', models.TextField(default='')),
                ('assessment_method', models.CharField(default='', max_length=200)),
                ('link', models.TextField(default='')),
                ('reference_system', models.CharField(default='', max_length=200)),
                ('threshold', models.IntegerField(default=0)),
                ('component_id', models.CharField(default='', max_length=200)),
                ('course_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='CurrentClient',
            fields=[
                ('coach', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('item', models.IntegerField(primary_key=True, serialize=False)),
                ('deadline_text', models.CharField(default='', max_length=200)),
                ('deadline_number', models.IntegerField()),
                ('name', models.CharField(default='', max_length=200)),
                ('component_id', models.CharField(default='', max_length=200)),
                ('component_type', models.CharField(default='', max_length=200)),
                ('assignment_type', models.CharField(default='', max_length=200)),
                ('title', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('matrix', models.CharField(default='', max_length=200)),
                ('resources', models.TextField(default='')),
                ('conditions', models.TextField(default='')),
                ('status', models.CharField(default='uncompleted', max_length=200)),
                ('completion_stamp', models.IntegerField(default=0)),
                ('completion_date', models.IntegerField(default=0)),
                ('submitting_user', models.CharField(default='', max_length=200)),
                ('reference', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('english', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('polish', models.CharField(default='', max_length=200)),
                ('publicating_user', models.CharField(default='', max_length=200)),
                ('publication_date', models.IntegerField()),
                ('deck', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField(default=0)),
                ('date_number', models.IntegerField(default=0)),
                ('student', models.CharField(default='', max_length=200)),
                ('course', models.CharField(default='', max_length=200)),
                ('result', models.IntegerField(default=0)),
                ('grade_type', models.CharField(default='', max_length=200)),
                ('examiner', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('position_number', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.TextField(default='')),
                ('wordcount', models.IntegerField()),
                ('link', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('title', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('content', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Matrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matrix', models.CharField(default='', max_length=200)),
                ('limit_number', models.IntegerField()),
                ('component_id', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publication_stamp', models.IntegerField()),
                ('publication_date', models.IntegerField()),
                ('coach', models.CharField(default='', max_length=200)),
                ('name', models.CharField(default='', max_length=200)),
                ('prompt', models.CharField(default='', max_length=200)),
                ('left_option', models.CharField(default='', max_length=200)),
                ('right_option', models.CharField(default='', max_length=200)),
                ('due_date', models.IntegerField()),
                ('number_of_reviews', models.IntegerField()),
                ('answers', models.TextField(default='')),
                ('revision_days', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_id', models.CharField(default='', max_length=200)),
                ('component_type', models.CharField(default='', max_length=200)),
                ('title', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('resources', models.TextField(default='')),
                ('conditions', models.TextField(default='')),
                ('reference', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('stamp', models.IntegerField(default=0)),
                ('sender', models.CharField(default='', max_length=200)),
                ('recipient', models.CharField(default='', max_length=200)),
                ('subject', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('notification_type', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField(default=0)),
                ('date_number', models.IntegerField(default=0)),
                ('command', models.CharField(default='', max_length=200)),
                ('value', models.CharField(default='', max_length=200)),
                ('author', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('name', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('display_name', models.CharField(default='', max_length=200)),
                ('avatar', models.URLField()),
                ('current_english_level', models.CharField(default='', max_length=200)),
                ('current_semester', models.IntegerField(default=1)),
                ('current_specialization', models.CharField(default='', max_length=200)),
                ('current_degree', models.CharField(default='', max_length=200)),
                ('early_admission', models.IntegerField(default=1)),
                ('semester_1_status', models.CharField(default='', max_length=200)),
                ('semester_2_status', models.CharField(default='', max_length=200)),
                ('semester_3_status', models.CharField(default='', max_length=200)),
                ('semester_4_status', models.CharField(default='', max_length=200)),
                ('semester_5_status', models.CharField(default='', max_length=200)),
                ('semester_6_status', models.CharField(default='', max_length=200)),
                ('semester_7_status', models.CharField(default='', max_length=200)),
                ('semester_8_status', models.CharField(default='', max_length=200)),
                ('semester_9_status', models.CharField(default='', max_length=200)),
                ('semester_10_status', models.CharField(default='', max_length=200)),
                ('semester_11_status', models.CharField(default='', max_length=200)),
                ('semester_12_status', models.CharField(default='', max_length=200)),
                ('semester_13_status', models.CharField(default='', max_length=200)),
                ('semester_14_status', models.CharField(default='', max_length=200)),
                ('semester_15_status', models.CharField(default='', max_length=200)),
                ('semester_16_status', models.CharField(default='', max_length=200)),
                ('associates_degree_status', models.CharField(default='', max_length=200)),
                ('bachelors_degree_status', models.CharField(default='', max_length=200)),
                ('masters_degree_status', models.CharField(default='', max_length=200)),
                ('doctorate_degree_status', models.CharField(default='', max_length=200)),
                ('professors_title_status', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_name', models.CharField(default='', max_length=200)),
                ('description', models.TextField(default='')),
                ('courses', models.CharField(default='', max_length=200)),
                ('degree', models.CharField(default='', max_length=200)),
                ('image', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('description', models.CharField(default='', max_length=200)),
                ('question', models.CharField(default='', max_length=200)),
                ('answer_a', models.CharField(default='', max_length=200)),
                ('answer_b', models.CharField(default='', max_length=200)),
                ('answer_c', models.CharField(default='', max_length=200)),
                ('answer_d', models.CharField(default='', max_length=200)),
                ('correct_answer', models.CharField(default='', max_length=200)),
                ('question_type', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quiz_id', models.IntegerField(default=0)),
                ('question_id', models.IntegerField(default=0)),
                ('client', models.CharField(default='', max_length=200)),
                ('answer', models.CharField(default='', max_length=200)),
                ('result', models.CharField(default='', max_length=200)),
                ('date_number', models.IntegerField(default=0)),
                ('status', models.CharField(default='', max_length=200)),
                ('quiz_question_id', models.IntegerField(default=0)),
                ('collection_name', models.CharField(default='', max_length=200)),
                ('collection_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Repertoire',
            fields=[
                ('title', models.CharField(default='', max_length=200, primary_key=True, serialize=False)),
                ('duration', models.IntegerField()),
                ('title_type', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RepertoireLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField()),
                ('date', models.IntegerField()),
                ('name', models.CharField(default='', max_length=200)),
                ('title', models.CharField(default='', max_length=200)),
                ('number_of_episodes', models.IntegerField()),
                ('status', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Roadmap',
            fields=[
                ('roadmap_id_number', models.AutoField(primary_key=True, serialize=False)),
                ('roadmap_matrix', models.CharField(default='', max_length=200)),
                ('semester', models.IntegerField(default=0)),
                ('course', models.CharField(default='', max_length=200)),
                ('name', models.CharField(default='', max_length=200)),
                ('deadline_number', models.IntegerField(default=0)),
                ('planning_user', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
                ('item', models.IntegerField(default=0)),
                ('status_type', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SentenceStock',
            fields=[
                ('sentence_id', models.IntegerField(primary_key=True, serialize=False)),
                ('polish', models.TextField(default='')),
                ('english', models.TextField(default='')),
                ('glossary', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_name', models.CharField(default='', max_length=200)),
                ('sentence_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Spin',
            fields=[
                ('scene', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('message', models.TextField(default='')),
                ('option_a_text', models.CharField(default='', max_length=200)),
                ('option_b_text', models.CharField(default='', max_length=200)),
                ('option_c_text', models.CharField(default='', max_length=200)),
                ('option_d_text', models.CharField(default='', max_length=200)),
                ('option_a_view', models.IntegerField(default=0)),
                ('option_b_view', models.IntegerField(default=0)),
                ('option_c_view', models.IntegerField(default=0)),
                ('option_d_view', models.IntegerField(default=0)),
                ('option_key', models.CharField(default='', max_length=200)),
                ('option_a_value', models.CharField(default='', max_length=200)),
                ('option_b_value', models.CharField(default='', max_length=200)),
                ('option_c_value', models.CharField(default='', max_length=200)),
                ('option_d_value', models.CharField(default='', max_length=200)),
                ('view_type', models.CharField(default='', max_length=200)),
                ('story', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watchword', models.IntegerField(default=0)),
                ('cue', models.CharField(default='', max_length=200)),
                ('response', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField()),
                ('date_number', models.IntegerField()),
                ('date', models.CharField(default='', max_length=200)),
                ('name', models.CharField(default='', max_length=200)),
                ('command', models.CharField(default='', max_length=200)),
                ('value', models.CharField(default='', max_length=200)),
                ('stream_user', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='active', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('unique_id', models.AutoField(primary_key=True, serialize=False)),
                ('stamp', models.IntegerField()),
                ('date_number', models.IntegerField()),
                ('date', models.CharField(default='', max_length=200)),
                ('item', models.IntegerField()),
                ('name', models.CharField(default='', max_length=200)),
                ('assignment_type', models.CharField(default='', max_length=200)),
                ('title', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('wordcount', models.IntegerField()),
                ('status', models.CharField(default='submitted', max_length=200)),
                ('reviewed_content', models.TextField(default='')),
                ('flagged_content', models.TextField(default='')),
                ('analysis', models.TextField(default='')),
                ('minor_errors', models.IntegerField(default=0)),
                ('major_errors', models.IntegerField(default=0)),
                ('reviewing_user', models.CharField(default='', max_length=200)),
                ('revision_date', models.IntegerField(default=0)),
                ('conditions', models.TextField(default='')),
                ('comment', models.TextField(default='')),
                ('grade', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Pronunciation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publication_stamp', models.IntegerField()),
                ('publication_date', models.IntegerField()),
                ('coach', models.CharField(default='', max_length=200)),
                ('name', models.CharField(default='', max_length=200)),
                ('entry', models.CharField(default='', max_length=200)),
                ('due_date', models.IntegerField()),
                ('number_of_reviews', models.IntegerField()),
                ('answers', models.TextField(default='')),
                ('revision_days', models.TextField(default='')),
            ],
            options={
                'unique_together': {('name', 'entry')},
            },
        ),
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.CharField(default='', max_length=200)),
                ('parent', models.CharField(default='', max_length=200)),
                ('pattern', models.CharField(default='', max_length=200)),
            ],
            options={
                'unique_together': {('prompt', 'parent')},
            },
        ),
        migrations.CreateModel(
            name='LibraryLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('link', models.TextField(default='')),
                ('status', models.CharField(default='', max_length=200)),
            ],
            options={
                'unique_together': {('name', 'link')},
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('english', models.CharField(default='', max_length=200)),
                ('polish', models.CharField(default='', max_length=200)),
                ('publication_date', models.IntegerField()),
                ('publicating_user', models.CharField(default='', max_length=200)),
                ('translation_date', models.IntegerField()),
                ('translating_user', models.CharField(default='', max_length=200)),
                ('revision_date', models.IntegerField()),
                ('reviewing_user', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
                ('deck', models.CharField(default='', max_length=200)),
            ],
            options={
                'unique_together': {('name', 'english')},
            },
        ),
    ]
