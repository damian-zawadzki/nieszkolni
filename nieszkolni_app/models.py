from django.db import models


class Card(models.Model):
    card_id = models.IntegerField(primary_key=True)
    client = models.CharField(max_length=200)
    deck = models.CharField(max_length=200)
    english = models.CharField(max_length=200)
    polish = models.CharField(max_length=200)
    publication_date = models.IntegerField()
    due_date = models.IntegerField()
    interval = models.IntegerField()
    number_of_reviews = models.IntegerField()
    answers = models.TextField(default="")
    card_opening_times = models.TextField(default="")
    card_closing_times = models.TextField(default="")
    durations = models.TextField(default="")
    card_revision_days = models.TextField(default="")
    line = models.IntegerField()
    coach = models.CharField(max_length=200)


class Client(models.Model):
    # Global settings
    user_type = models.CharField(max_length=200, default="client")
    name = models.CharField(max_length=200, default="", primary_key=True)
    phone_number = models.IntegerField(default=987654321)
    contact_email_address = models.CharField(max_length=200, default="")
    school = models.CharField(max_length=200, default="-")
    internal_email_address = models.CharField(max_length=200, default="")
    meeting_duration = models.IntegerField(default=55)
    price = models.IntegerField(default=0)
    acquisition_channel = models.CharField(max_length=200, default="")
    recommenders = models.CharField(max_length=200, default="")
    reasons_for_resignation = models.CharField(max_length=200, default="")

    status = models.CharField(max_length=200, default="")
    coach = models.CharField(max_length=200, default="")
    level = models.CharField(max_length=200, default="")

    # Private settings
    daily_limit_of_new_cards = models.IntegerField(default=25, null=True)


class Submission(models.Model):
    unique_id = models.AutoField(primary_key=True)
    stamp = models.IntegerField()
    date_number = models.IntegerField()
    date = models.CharField(max_length=200, default="")
    item = models.IntegerField()
    name = models.CharField(max_length=200, default="")
    assignment_type = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=200, default="")
    content = models.TextField(default="")
    wordcount = models.IntegerField()
    status = models.CharField(max_length=200, default="submitted")
    reviewed_content = models.TextField(default="")
    flagged_content = models.TextField(default="")
    analysis = models.TextField(default="")
    minor_errors = models.IntegerField(default=0)
    major_errors = models.IntegerField(default=0)
    reviewing_user = models.CharField(max_length=200, default="")
    revision_date = models.IntegerField()
    conditions = models.TextField(default="")
    comment = models.TextField(default="")
    grade = models.CharField(max_length=200, default="")


class Curriculum(models.Model):
    item = models.IntegerField(primary_key=True)
    deadline_text = models.CharField(max_length=200, default="")
    deadline_number = models.IntegerField()
    name = models.CharField(max_length=200, default="")
    component_id = models.CharField(max_length=200, default="")
    component_type = models.CharField(max_length=200, default="")
    assignment_type = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=200, default="")
    content = models.TextField(default="")
    matrix = models.CharField(max_length=200, default="")
    resources = models.TextField(default="")
    conditions = models.TextField(default="")
    status = models.CharField(max_length=200, default="uncompleted")
    completion_stamp = models.IntegerField(default=0)
    completion_date = models.IntegerField(default=0)
    submitting_user = models.CharField(max_length=200, default="")
    reference = models.IntegerField(default=0)


class Matrix(models.Model):
    matrix = models.CharField(max_length=200, default="")
    limit_number = models.IntegerField()
    component_id = models.CharField(max_length=200, default="")


class Module(models.Model):
    component_id = models.CharField(max_length=200, default="")
    component_type = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=200, default="")
    content = models.TextField(default="")
    resources = models.TextField(default="")
    conditions = models.TextField(default="")


class CurrentClient(models.Model):
    coach = models.CharField(max_length=200, default="", primary_key=True)
    name = models.CharField(max_length=200, default="")


class Pronunciation(models.Model):
    class Meta:
        unique_together = (("name", "entry"),)

    publication_stamp = models.IntegerField()
    publication_date = models.IntegerField()
    coach = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    entry = models.CharField(max_length=200, default="")
    due_date = models.IntegerField()
    number_of_reviews = models.IntegerField()
    answers = models.TextField(default="")
    revision_days = models.TextField(default="")


class Dictionary(models.Model):
    english = models.CharField(max_length=200, default="", primary_key=True)
    polish = models.CharField(max_length=200, default="")
    publicating_user = models.CharField(max_length=200, default="")
    publication_date = models.IntegerField()
    deck = models.CharField(max_length=200, default="")


class Book(models.Model):
    class Meta:
        unique_together = (("name", "english"),)

    name = models.CharField(max_length=200, default="")
    english = models.CharField(max_length=200, default="")
    polish = models.CharField(max_length=200, default="")
    publication_date = models.IntegerField()
    publicating_user = models.CharField(max_length=200, default="")
    translation_date = models.IntegerField()
    translating_user = models.CharField(max_length=200, default="")
    revision_date = models.IntegerField()
    reviewing_user = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="")
    deck = models.CharField(max_length=200, default="")


class Catalogue(models.Model):
    publication_date = models.IntegerField()
    publicating_user = models.CharField(max_length=200, default="")
    entry = models.CharField(max_length=200, default="")
    entry_number = models.IntegerField()
    catalogue_number = models.IntegerField()
    catalogue_name = models.CharField(max_length=200, default="")


class Prompt(models.Model):
    class Meta:
        unique_together = (("prompt", "parent"),)

    prompt = models.CharField(max_length=200, default="")
    parent = models.CharField(max_length=200, default="")
    pattern = models.CharField(max_length=200, default="")


class Memory(models.Model):
    publication_stamp = models.IntegerField()
    publication_date = models.IntegerField()
    coach = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    prompt = models.CharField(max_length=200, default="")
    left_option = models.CharField(max_length=200, default="")
    right_option = models.CharField(max_length=200, default="")
    due_date = models.IntegerField()
    number_of_reviews = models.IntegerField()
    answers = models.TextField(default="")
    revision_days = models.TextField(default="")


class Stream(models.Model):
    stamp = models.IntegerField()
    date_number = models.IntegerField()
    date = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    command = models.CharField(max_length=200, default="")
    value = models.CharField(max_length=200, default="")
    stream_user = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="active")


class SentenceStock(models.Model):
    sentence_id = models.IntegerField(primary_key=True)
    polish = models.TextField(default="")
    english = models.TextField(default="")
    glossary = models.TextField(default="")


class Composer(models.Model):
    list_number = models.IntegerField()
    sentence_number = models.IntegerField(primary_key=True)
    sentence_id = models.IntegerField()
    name = models.CharField(max_length=200, default="")
    polish = models.TextField(default="")
    english = models.TextField(default="")
    glossary = models.TextField(default="")
    submission_stamp = models.IntegerField()
    submission_date = models.IntegerField()
    status = models.CharField(max_length=200, default="")
    translation = models.TextField(default="")
    result = models.CharField(max_length=200, default="")
    reviewing_user = models.CharField(max_length=200, default="")


class Set(models.Model):
    set_name = models.CharField(max_length=200, default="")
    sentence_id = models.IntegerField()


class Library(models.Model):
    position_number = models.IntegerField(primary_key=True)
    title = models.TextField(default="")
    wordcount = models.IntegerField()
    link = models.TextField(default="")


class LibraryLine(models.Model):
    class Meta:
        unique_together = (("name", "link"),)

    name = models.CharField(max_length=200, default="")
    link = models.TextField(default="")
    status = models.CharField(max_length=200, default="")


class Repertoire(models.Model):
    title = models.CharField(max_length=200, default="", primary_key=True)
    duration = models.IntegerField()
    title_type = models.CharField(max_length=200, default="")


class RepertoireLine(models.Model):
    stamp = models.IntegerField()
    date = models.IntegerField()
    name = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=200, default="")
    number_of_episodes = models.IntegerField()
    status = models.CharField(max_length=200, default="")


class Profile(models.Model):
    name = models.CharField(max_length=200, default="", primary_key=True)
    display_name = models.CharField(max_length=200, default="")
    avatar = models.URLField(max_length=200)
    current_english_level = models.CharField(max_length=200, default="")
    current_semester = models.IntegerField(default=1)
    current_specialization = models.CharField(max_length=200, default="")
    current_degree = models.CharField(max_length=200, default="")
    early_admission = models.IntegerField(default=1)
    semester_1_status = models.CharField(max_length=200, default="")
    semester_2_status = models.CharField(max_length=200, default="")
    semester_3_status = models.CharField(max_length=200, default="")
    semester_4_status = models.CharField(max_length=200, default="")
    semester_5_status = models.CharField(max_length=200, default="")
    semester_6_status = models.CharField(max_length=200, default="")
    semester_7_status = models.CharField(max_length=200, default="")
    semester_8_status = models.CharField(max_length=200, default="")
    semester_9_status = models.CharField(max_length=200, default="")
    semester_10_status = models.CharField(max_length=200, default="")
    semester_11_status = models.CharField(max_length=200, default="")
    semester_12_status = models.CharField(max_length=200, default="")
    semester_13_status = models.CharField(max_length=200, default="")
    semester_14_status = models.CharField(max_length=200, default="")
    semester_15_status = models.CharField(max_length=200, default="")
    semester_16_status = models.CharField(max_length=200, default="")
    associates_degree_status = models.CharField(max_length=200, default="")
    bachelors_degree_status = models.CharField(max_length=200, default="")
    masters_degree_status = models.CharField(max_length=200, default="")
    doctorate_degree_status = models.CharField(max_length=200, default="")
    professors_title_status = models.CharField(max_length=200, default="")


class Roadmap(models.Model):
    roadmap_id_number = models.AutoField(primary_key=True)
    roadmap_matrix = models.CharField(max_length=200, default="")
    semester = models.IntegerField(default=0)
    course = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    deadline_number = models.IntegerField(default=0)
    planning_user = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="")


class Course(models.Model):
    course = models.CharField(max_length=200, primary_key=True)
    course_type = models.CharField(max_length=200, default="")
    course_description = models.TextField(default="")
    registration_description = models.TextField(default="")
    assessment_description = models.TextField(default="")
    assessment_method = models.CharField(max_length=200, default="")
    link = models.TextField(default="")
    reference_system = models.CharField(max_length=200, default="")
    threshold = models.IntegerField(default=0)


class Grade(models.Model):
    stamp = models.IntegerField(default=0)
    date_number = models.IntegerField(default=0)
    student = models.CharField(max_length=200, default="")
    course = models.CharField(max_length=200, default="")
    result = models.IntegerField(default=0)
    grade_type = models.CharField(max_length=200, default="")
    examiner = models.CharField(max_length=200, default="")


class Material(models.Model):
    title = models.CharField(max_length=200, default="", primary_key=True)
    content = models.TextField(default="")


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    stamp = models.IntegerField(default=0)
    sender = models.CharField(max_length=200, default="")
    recipient = models.CharField(max_length=200, default="")
    subject = models.CharField(max_length=200, default="")
    content = models.TextField(default="")
    notification_type = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="")


class Option(models.Model):
    stamp = models.IntegerField(default=0)
    date_number = models.IntegerField(default=0)
    command = models.CharField(max_length=200, default="")
    value = models.CharField(max_length=200, default="")
    author = models.CharField(max_length=200, default="")