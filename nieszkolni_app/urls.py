from django.contrib import admin
from django.urls import path, re_path, include

from .views import views
from .views import staff_views

urlpatterns = [
    path('', views.welcome, name="welcome"),

    # Campus
    path(
        'campus/',
        views.campus,
        name="campus"
        ),
    path(
        'lightbox_results/',
        views.lightbox_results,
        name="lightbox_results"
        ),

    path('vocabulary/', views.vocabulary, name="vocabulary"),
    path('sentences/', views.sentences, name="sentences"),
    path('congratulations/', views.congratulations, name="congratulations"),
    path('options/', views.options, name="options"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('office/', views.office, name="office"),
    path('staff/', views.staff, name="staff"),
    path('management/', views.management, name="management"),
    path('old_staff/', views.old_staff, name="old_staff"),
    path('profile/', views.profile, name="profile"),
    path('portrait/<str:client>/', views.portrait, name="portrait"),
    path('profile_introduction/', views.profile_introduction, name="profile_introduction"),
    path('profile_menu/', views.profile_menu, name="profile_menu"),
    path('register_user/', views.register_user, name="register_user"),
    path('register_client/', views.register_client, name="register_client"),
    path('list_current_users/', views.list_current_users, name="list_current_users"),
    path('display_user/<str:client>', views.display_user, name="display_user"),
    path('submit_assignment/', views.submit_assignment, name="submit_assignment"),
    path('submit_assignment/<int:item>/', views.submit_assignment, name="submit_assignment"),
    path('upload_curriculum/', views.upload_curriculum, name="upload_curriculum"),
    path('add_curriculum/', views.add_curriculum, name="add_curriculum"),
    path('add_curriculum/<str:client>/', views.add_curriculum, name="add_curriculum"),
    path('add_multiple_curricula/', views.add_multiple_curricula, name="add_multiple_curricula"),
    path('add_multiple_curricula_2/<str:component_id>/', views.add_multiple_curricula_2, name="add_multiple_curricula_2"),
    path('remove_multiple_curricula/', views.remove_multiple_curricula, name="remove_multiple_curricula"),    
    path('add_matrix/', views.add_matrix, name="add_matrix"),
    path('display_matrices/', views.display_matrices, name="display_matrices"),
    path('plan_matrix/', views.plan_matrix, name="plan_matrix"),
    path('update_matrix/<str:matrix>/', views.update_matrix, name="update_matrix"),
    path('choose_component/', views.choose_component, name="choose_component"),
    path('choose_id_prefix/<str:component>/', views.choose_id_prefix, name="choose_id_prefix"),
    path('choose_reference/<str:component>/<int:id_prefix>/', views.choose_reference, name="choose_reference"),
    path('choose_resources/<str:component>/<int:id_prefix>/<int:reference>/', views.choose_resources, name="choose_resources"),
    path('add_module/<str:component>/<int:id_prefix>/<int:reference>/<path:resources>/', views.add_module, name="add_module"),
    path('update_module/<str:component_id>/', views.update_module, name="update_module"),
    path('display_modules/', views.display_modules, name="display_modules"),
    path('assignments/', views.assignments, name="assignments"),
    path('assignments/<str:client>/', views.assignments, name="assignments"),
    path('assignment/', views.assignment, name="assignment"),
    path('assignment/<str:item>/', views.assignment, name="assignment"),
    path('submit_assignment_automatically/', views.submit_assignment_automatically, name="submit_assignment_automatically"),
    path('submit_assignment_automatically/<int:item>/', views.submit_assignment_automatically, name="submit_assignment_automatically"),
    path('list_of_submissions/', views.list_of_submissions, name="list_of_submissions"),
    path('list_of_assignments_to_grade/', views.list_of_assignments_to_grade, name="list_of_assignments_to_grade"),
    path('grade_assignment/<int:unique_id>', views.grade_assignment, name="grade_assignment"),
    path('footer/', views.footer, name="footer"),
    path('display_curricula/<str:client>', views.display_curricula, name="display_curricula"),
    path('coach/', views.coach, name="coach"),
    path('teacher/', views.teacher, name="teacher"),
    path('coach_menu/', views.coach_menu, name="coach_menu"),
    path('session_mode/', views.session_mode, name="session_mode"),
    path('agenda/', views.agenda, name="agenda"),
    path('check_homework/', views.check_homework, name="check_homework"),
    path('check_homework/<str:current_user>/', views.check_homework, name="check_homework"),
    path('switch_clients/', views.switch_clients, name="switch_clients"),
    path('my_pronunciation/', views.my_pronunciation, name="my_pronunciation"),
    path('upload_pronunciation/', views.upload_pronunciation, name="upload_pronunciation"),
    path('upload_dictionary/', views.upload_dictionary, name="upload_dictionary"),
    path('upload_catalogues/', views.upload_catalogues, name="upload_catalogues"),
    path('upload_sentence_stock/', views.upload_sentence_stock, name="upload_sentence_stock"),
    path('sentence_stock/', views.sentence_stock, name="sentence_stock"),
    path('update_sentence_stock/', views.update_sentence_stock, name="update_sentence_stock"),
    path('add_to_sentence_stock/', views.add_to_sentence_stock, name="add_to_sentence_stock"),
    path('choose_set_type/', views.choose_set_type, name="choose_set_type"),
    path('compose_set/<str:set_type>/', views.compose_set, name="compose_set"),
    path('display_sets/', views.display_sets, name="display_sets"),
    path('display_set/<int:set_id>/', views.display_set, name="display_set"),
    path('composer/', views.composer, name="composer"),
    path('upload_composer/', views.upload_composer, name="upload_composer"),
    path('composed_sentences/', views.composed_sentences, name="composed_sentences"),
    path('grade_sentences/', views.grade_sentences, name="grade_sentences"),
    path('label_sentences/', views.label_sentences, name="label_sentences"),
    path('dictionary/', views.dictionary, name="dictionary"),
    path('translate_wordbook/', views.translate_wordbook, name="translate_wordbook"),
    path('approve_wordbook/', views.approve_wordbook, name="approve_wordbook"),
    path('translate_sentencebook/', views.translate_sentencebook, name="translate_sentencebook"),
    path('approve_sentencebook/', views.approve_sentencebook, name="approve_sentencebook"),
    path('review_book/', views.review_book, name="review_book"),
    path('upload_anki/', views.upload_anki, name="upload_anki"),
    path('catalogues/', views.catalogues, name="catalogues"),
    path('catalogues_list_of_phrases/', views.catalogues_list_of_phrases, name="catalogues_list_of_phrases"),
    path('prompts/', views.prompts, name="prompts"),
    path('memories/', views.memories, name="memories"),
    path('upload_memories/', views.upload_memories, name="upload_memories"),
    path('display_memories/', views.display_memories, name="display_memories"),
    path('display_memory/<int:unique_id>/', views.display_memory, name="display_memory"),
    path('stream/', views.stream, name="stream"),
    path('add_stream/', views.add_stream, name="add_stream"),
    path('remove_from_stream/', views.remove_from_stream, name="remove_from_stream"),
    path('stream/<int:start>/<int:end>', views.stream, name="stream"),
    path('client_stream/', views.client_stream, name="client_stream"),
    path('upload_stream/', views.upload_stream, name="upload_stream"),
    path('library/', views.library, name="library"),
    path('library_line/', views.library_line, name="library_line"),
    path('report_reading/', views.report_reading, name="report_reading"),
    path('repertoire/', views.repertoire, name="repertoire"),
    path('repertoire_line/', views.repertoire_line, name="repertoire_line"),
    path('report_listening/', views.report_listening, name="report_listening"),
    path('download_assignments/', views.download_assignments, name="download_assignments"),
    path('add_course/', views.add_course, name="add_course"),
    path('list_courses/', views.list_courses, name="list_courses"),
    path('add_roadmap/', views.add_roadmap, name="add_roadmap"),
    path('update_roadmap/', views.update_roadmap, name="update_roadmap"),
    path('display_roadmap_details/<int:course_id>', views.display_roadmap_details, name="display_roadmap_details"),
    path('add_profile/', views.add_profile, name="add_profile"),
    path('profiles/', views.profiles, name="profiles"),
    path('display_profile/<str:client>', views.display_profile, name="display_profile"),
    path('update_profile/', views.update_profile, name="update_profile"),
    path('roadmaps/', views.roadmaps, name="roadmaps"),
    path('roadmaps/<str:client_name>/<int:semester>/', views.roadmaps, name="roadmaps"),
    path('add_material/', views.add_material, name="add_material"),
    path('materials/', views.materials, name="materials"),
    path('display_material/', views.display_material, name="display_material"),
    path('ranking/', views.ranking, name="ranking"),
    path('my_statistics/', views.my_statistics, name="my_statistics"),
    path('notifications/', views.notifications, name="notifications"),
    path('announcements/', views.announcements, name="announcements"),
    path('make_announcement/', views.make_announcement, name="make_announcement"),
    path('announcement/<int:notification_id>/', views.announcement, name="announcement"),
    path('update_announcement/<int:notification_id>/', views.update_announcement, name="update_announcement"),
    path('announcement/', views.announcement, name="announcement"),
    path('add_grade/', views.add_grade, name="add_grade"),
    path('results/', views.results, name="results"),
    path('grade/<int:grade_id>', views.grade, name="grade"),
    path('add_option/', views.add_option, name="add_option"),
    path('display_options/', views.display_options, name="display_options"),
    path('add_question/', views.add_question, name="add_question"),
    path('display_questions/', views.display_questions, name="display_questions"),
    path('add_collection/', views.add_collection, name="add_collection"),
    path('display_collection/', views.display_collection, name="display_collection"),
    path('display_quizzes/', views.display_quizzes, name="display_quizzes"),
    path('take_quiz/<int:item>/', views.take_quiz, name="take_quiz"),
    path('add_spin/', views.add_spin, name="add_spin"),
    path('update_spin/<int:scene>/', views.update_spin, name="update_spin"),
    path('display_spin/<str:client>/<int:story>/', views.display_spin, name="display_spin"),
    path('display_spin/<str:client>/<int:story>/<int:scene>/', views.display_spin, name="display_spin"),
    path('display_spin/<str:client>/<int:story>/<int:scene>/<int:watchword>/', views.display_spin, name="display_spin"),
    path('display_story/', views.display_story, name="display_story"),
    path('rules/', views.rules, name="rules"),
    path('add_program/', views.add_program, name="add_program"),
    path('manage_programs_and_courses/', views.manage_programs_and_courses, name="manage_programs_and_courses"),
    path('programs/', views.programs, name="programs"),
    path('program/<int:program_id>/', views.program, name="program"),
    path('update_program/<int:program_id>/', views.update_program, name="update_program"),
    path('plan_program/', views.plan_program, name="plan_program"),
    path('courses/', views.courses, name="courses"),
    path('course/<int:course_id>/', views.course, name="course"),
    path('add_id_prefix/', views.add_id_prefix, name="add_id_prefix"),
    path('display_prefixes/', views.display_prefixes, name="display_prefixes"),
    path('add_ticket/', views.add_ticket, name="add_ticket"),
    path('display_open_tickets/', views.display_open_tickets, name="display_open_tickets"),
    path('display_closed_tickets/', views.display_closed_tickets, name="display_closed_tickets"),
    path('display_ticket/<int:ticket_id>/', views.display_ticket, name="display_ticket"),
    path('add_category/', views.add_category, name="add_category"),
    path('display_categories/', views.display_categories, name="display_categories"),
    path('clock/', views.clock, name="clock"),
    path('manual_clock/', views.manual_clock, name="manual_clock"),
    path('timesheet/', views.timesheet, name="timesheet"),
    path('update_timesheet/', views.update_timesheet, name="update_timesheet"),
    path('upload_timesheet/', views.upload_timesheet, name="upload_timesheet"),
    path('onboard_client/', views.onboard_client, name="onboard_client"),
    path('weekly_checklist/', views.weekly_checklist, name="weekly_checklist"),
    path('examination_mode/', views.examination_mode, name="examination_mode"),
    path('rating/<str:client>/<str:category>/<int:position>/', views.rating, name="rating"),
    path('ratings/', views.ratings, name="ratings"),
    path('inspection/', views.inspection, name="inspection"),
    path('mychart/', views.mychart, name="mychart"),
    path('add_challenge/', views.add_challenge, name="add_challenge"),
    path('display_challenge_matrices/', views.display_challenge_matrices, name="display_challenge_matrices"),
    path('display_challenges/<int:matrix_id>/', views.display_challenges, name="display_challenges"),
    path('display_challenge/<int:challenge_id>/', views.display_challenge, name="display_challenge"),
    path('update_challenge/<int:challenge_id>/', views.update_challenge, name="update_challenge"),
    path('challenges/', views.challenges, name="challenges"),
    path('challenges/<int:unique_id>/', views.challenges, name="challenges"),
    path('challenge/<int:challenge_id>/', views.challenge, name="challenge"),
    path('display_challenge_sets/', views.display_challenge_sets, name="display_challenge_sets"),
    path('display_challenge_set/<int:process_number>/', views.display_challenge_set, name="display_challenge_set"),
    path('translate_sentences/<int:item>/', views.translate_sentences, name="translate_sentences"),
    path('applause/<int:activity_points>/', views.applause, name="applause"),

    # Client
    path(
        'my_grades/<str:client>',
        views.my_grades,
        name="my_grades"
        ),
    path(
        'my_final_grades/<str:client>',
        views.my_final_grades,
        name="my_final_grades"
        ),
    path(
        'my_activity_points/<str:client>',
        views.my_activity_points,
        name="my_activity_points"
        ),
    path(
        'my_deadlines/<str:client>',
        views.my_deadlines,
        name="my_deadlines"
        ),

    # Surveys
    path(
        'survey_process/',
        staff_views.survey_process,
        name="survey_process"
        ),
    path(
        'add_survey_option/',
        staff_views.add_survey_option,
        name="add_survey_option"
        ),
    path(
        'add_survey_question/',
        staff_views.add_survey_question,
        name="add_survey_question"
        ),
    path(
        'display_survey_question/<int:question_id>/',
        staff_views.display_survey_question,
        name="display_survey_question"
        ),
    path(
        'add_survey/',
        staff_views.add_survey,
        name="add_survey"
        ),
    path(
        'display_surveys/',
        staff_views.display_surveys,
        name="display_surveys"
        ),
    path(
        'display_survey/<int:survey_id>/',
        staff_views.display_survey,
        name="display_survey"
        ),
    path(
        'add_question_to_survey/',
        staff_views.add_question_to_survey,
        name="add_question_to_survey"
        ),
    path(
        'survey/<int:item>/',
        staff_views.survey,
        name="survey"
        ),
    path(
        'completed/',
        staff_views.completed,
        name="completed"
        ),
    path(
        'responses/',
        staff_views.responses,
        name="responses"
        ),

    path('my_courses/', views.my_courses, name="my_courses"),
    path('bill/', views.bill, name="bill"),
    path('flashcard/<str:username>/<str:deck>/', views.flashcard, name="flashcard"),
    
    path('card/<str:client>/<int:card_id>/', views.card, name="card"),
    path('analytics_entries_per_student/<str:coach>/', views.analytics_entries_per_student, name="analytics_entries_per_student"),
    path('analytics_entries/', views.analytics_entries, name="analytics_entries"),
    path('analytics_activity/', views.analytics_activity, name="analytics_activity"),
    path('analytics_indicators/', views.analytics_indicators, name="analytics_indicators"),
    path('analytics_grades/', views.analytics_grades, name="analytics_grades"),
    path('lab/', views.lab, name="lab"),
    path('voice/', views.voice, name="voice"),
    path('deans_office/', views.deans_office, name="deans_office"),
    path('hall_of_fame/', views.hall_of_fame, name="hall_of_fame"),
    path('remove_all_new_cards/', views.remove_all_new_cards, name="remove_all_new_cards"),
    path('remove_profile/', views.remove_profile, name="remove_profile"),
    path('remove_client/', views.remove_client, name="remove_client"),
    path('remove_multiple_from_stream/', views.remove_multiple_from_stream, name="remove_multiple_from_stream"),
    re_path(r'^flashcard_question/$', views.flashcard_question, name='flashcard_question'),
    re_path(r'^flashcard_answer/$', views.flashcard_answer, name='flashcard_answer'),
    path(
        'analytics/',
        views.analytics,
        name="analytics"
        ),

    # Pronunciation
    path(
        'deactivate_pronunciation_entries/',
        views.deactivate_pronunciation_entries,
        name="deactivate_pronunciation_entries"
        ),


    # Product
    path(
        'product_process/',
        staff_views.product_process,
        name="product_process"
        ),
    path(
        'add_product/',
        staff_views.add_product,
        name="add_product"
        ),
    path(
        'products/',
        staff_views.products,
        name="products"
        ),
    path(
        'product/<int:product_id>',
        staff_views.product,
        name="product"
        ),
    path(
        'update_product/<int:product_id>',
        staff_views.update_product,
        name="update_product"
        ),

    # Card
    path(
        'card_process/',
        staff_views.card_process,
        name="card_process"
        ),
    path(
        'display_cards/',
        staff_views.display_cards,
        name="display_cards"
        ),
    path(
        'display_card/<int:card_id>',
        staff_views.display_card,
        name="display_card"
        ),
    path(
        'cards/<str:client>/',
        views.cards,
        name="cards"
        ),

    # Contest

    path(
        'contest_process/',
        views.contest_process,
        name="contest_process"
        ),

       ]