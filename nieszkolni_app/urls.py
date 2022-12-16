from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.welcome, name="welcome"),
    path('campus', views.campus, name="campus"),
    path('vocabulary.html', views.vocabulary, name="vocabulary"),
    path('sentences.html', views.sentences, name="sentences"),
    path('view_answer.html', views.view_answer, name="view_answer"),
    path('congratulations.html', views.congratulations, name="congratulations"),
    path('options.html', views.options, name="options"),
    path('login_user', views.login_user, name="login_user"),
    path('logout_user', views.logout_user, name="logout_user"),
    path('staff.html', views.staff, name="staff"),
    path('old_staff.html', views.old_staff, name="old_staff"),
    path('profile.html', views.profile, name="profile"),
    path('profile_introduction.html', views.profile_introduction, name="profile_introduction"),
    path('staff_menu.html', views.staff_menu, name="staff_menu"),
    path('profile_menu.html', views.profile_menu, name="profile_menu"),
    path('register_user.html', views.register_user, name="register_user"),
    path('register_client.html', views.register_client, name="register_client"),
    path('list_current_users.html', views.list_current_users, name="list_current_users"),
    path('submit_assignment.html', views.submit_assignment, name="submit_assignment"),
    path('upload_curriculum.html', views.upload_curriculum, name="upload_curriculum"),
    path('add_curriculum/', views.add_curriculum, name="add_curriculum"),
    path('add_curriculum/<str:client>', views.add_curriculum, name="add_curriculum"),
    path('add_multiple_curricula/', views.add_multiple_curricula, name="add_multiple_curricula"),
    path('add_multiple_curricula_2/<str:component_id>', views.add_multiple_curricula_2, name="add_multiple_curricula_2"),
    path('remove_multiple_curricula/', views.remove_multiple_curricula, name="remove_multiple_curricula"),    
    path('add_matrix.html', views.add_matrix, name="add_matrix"),
    path('display_matrices.html', views.display_matrices, name="display_matrices"),
    path('plan_matrix.html', views.plan_matrix, name="plan_matrix"),
    path('update_matrix/<str:matrix>', views.update_matrix, name="update_matrix"),
    path('choose_component.html', views.choose_component, name="choose_component"),
    path('choose_id_prefix/<str:component>', views.choose_id_prefix, name="choose_id_prefix"),
    path('choose_reference/<str:component>/<int:id_prefix>', views.choose_reference, name="choose_reference"),
    path('choose_resources/<str:component>/<int:id_prefix>/<int:reference>', views.choose_resources, name="choose_resources"),
    path('add_module/<str:component>/<int:id_prefix>/<int:reference>/<path:resources>', views.add_module, name="add_module"),
    path('update_module/<str:component_id>', views.update_module, name="update_module"),
    path('display_modules.html', views.display_modules, name="display_modules"),
    path('assignments.html', views.assignments, name="assignments"),
    path('assignment.html', views.assignment, name="assignment"),
    path('assignment/<str:item>', views.assignment, name="assignment"),
    path('submit_assignment_automatically.html.html', views.submit_assignment, name="submit_assignment_automatically"),
    path('list_of_submissions.html', views.list_of_submissions, name="list_of_submissions"),
    path('list_of_assignments_to_grade.html', views.list_of_assignments_to_grade, name="list_of_assignments_to_grade"),
    path('footer.html.html', views.footer, name="footer"),
    path('display_curricula.html', views.display_curricula, name="display_curricula"),
    path('coach.html', views.coach, name="coach"),
    path('coach_menu.html', views.coach_menu, name="coach_menu"),
    path('session_mode.html', views.session_mode, name="session_mode"),
    path('agenda.html', views.agenda, name="agenda"),
    path('check_homework.html', views.check_homework, name="check_homework"),
    path('switch_clients.html', views.switch_clients, name="switch_clients"),
    path('my_pronunciation.html', views.my_pronunciation, name="my_pronunciation"),
    path('upload_pronunciation.html', views.upload_pronunciation, name="upload_pronunciation"),
    path('upload_dictionary.html', views.upload_dictionary, name="upload_dictionary"),
    path('upload_catalogues.html', views.upload_catalogues, name="upload_catalogues"),
    path('upload_sentence_stock.html', views.upload_sentence_stock, name="upload_sentence_stock"),
    path('sentence_stock.html', views.sentence_stock, name="sentence_stock"),
    path('update_sentence_stock/', views.update_sentence_stock, name="update_sentence_stock"),
    path('add_to_sentence_stock.html', views.add_to_sentence_stock, name="add_to_sentence_stock"),
    path('compose_set.html', views.compose_set, name="compose_set"),
    path('display_sets.html', views.display_sets, name="display_sets"),
    path('display_set/<int:set_id>', views.display_set, name="display_set"),
    path('composer.html', views.composer, name="composer"),
    path('composed_sentences.html', views.composed_sentences, name="composed_sentences"),
    path('grade_sentences.html', views.grade_sentences, name="grade_sentences"),
    path('dictionary.html', views.dictionary, name="dictionary"),
    path('translate_wordbook.html', views.translate_wordbook, name="translate_wordbook"),
    path('approve_wordbook.html', views.approve_wordbook, name="approve_wordbook"),
    path('translate_sentencebook.html', views.translate_sentencebook, name="translate_sentencebook"),
    path('approve_sentencebook.html', views.approve_sentencebook, name="approve_sentencebook"),
    path('upload_anki.html', views.upload_anki, name="upload_anki"),
    path('edit_card.html', views.edit_card, name="edit_card"),
    path('catalogues.html', views.catalogues, name="catalogues"),
    path('catalogues_list_of_phrases.html', views.catalogues_list_of_phrases, name="catalogues_list_of_phrases"),
    path('prompts.html', views.prompts, name="prompts"),
    path('memories.html', views.memories, name="memories"),
    path('upload_memories.html', views.upload_memories, name="upload_memories"),
    path('display_memories/', views.display_memories, name="display_memories"),
    path('display_memory/<int:unique_id>', views.display_memory, name="display_memory"),
    path('stream.html', views.stream, name="stream"),
    path('client_stream/', views.client_stream, name="client_stream"),
    path('upload_stream.html', views.upload_stream, name="upload_stream"),
    path('library.html', views.library, name="library"),
    path('library_line.html', views.library_line, name="library_line"),
    path('report_reading.html', views.report_reading, name="report_reading"),
    path('repertoire.html', views.repertoire, name="repertoire"),
    path('repertoire_line.html', views.repertoire_line, name="repertoire_line"),
    path('report_listening.html', views.report_listening, name="report_listening"),
    path('download_assignments.html', views.download_assignments, name="download_assignments"),
    path('add_course.html', views.add_course, name="add_course"),
    path('list_courses.html', views.list_courses, name="list_courses"),
    path('add_roadmap.html', views.add_roadmap, name="add_roadmap"),
    path('update_roadmap.html', views.update_roadmap, name="update_roadmap"),
    path('display_roadmap_details.html', views.display_roadmap_details, name="display_roadmap_details"),
    path('add_profile.html', views.add_profile, name="add_profile"),
    path('profiles.html', views.profiles, name="profiles"),
    path('display_profile.html', views.display_profile, name="display_profile"),
    path('update_profile.html', views.update_profile, name="update_profile"),
    path('roadmaps.html', views.roadmaps, name="roadmaps"),
    path('roadmaps/<str:client_name>/<int:semester>', views.roadmaps, name="roadmaps"),
    path('add_material.html', views.add_material, name="add_material"),
    path('materials.html', views.materials, name="materials"),
    path('display_material.html', views.display_material, name="display_material"),
    path('ranking.html', views.ranking, name="ranking"),
    path('statistics.html', views.statistics, name="statistics"),
    path('notifications.html', views.notifications, name="notifications"),
    path('announcements.html', views.announcements, name="announcements"),
    path('add_notification.html', views.add_notification, name="add_notification"),
    path('display_announcement/<int:notification_id>', views.display_announcement, name="display_announcement"),
    path('display_announcement/', views.display_announcement, name="display_announcement"),
    path('add_grade', views.add_grade, name="add_grade"),
    path('add_option', views.add_option, name="add_option"),
    path('display_options', views.display_options, name="display_options"),
    path('add_question', views.add_question, name="add_question"),
    path('display_questions', views.display_questions, name="display_questions"),
    path('add_collection', views.add_collection, name="add_collection"),
    path('display_collection', views.display_collection, name="display_collection"),
    path('display_quizzes', views.display_quizzes, name="display_quizzes"),
    path('take_quiz/<int:quiz_question_id>/<int:item>', views.take_quiz, name="take_quiz"),
    path('add_spin.html', views.add_spin, name="add_spin"),
    path('update_spin/<int:scene>', views.update_spin, name="update_spin"),
    path('display_spin/<str:client>/<int:story>', views.display_spin, name="display_spin"),
    path('display_spin/<str:client>/<int:story>/<int:scene>', views.display_spin, name="display_spin"),
    path('display_spin/<str:client>/<int:story>/<int:scene>/<int:watchword>', views.display_spin, name="display_spin"),
    path('display_story.html', views.display_story, name="display_story"),
    path('rules.html', views.rules, name="rules"),
    path('add_program.html', views.add_program, name="add_program"),
    path('programs.html', views.programs, name="programs"),
    path('program/<int:program_id>', views.program, name="program"),
    path('update_program/<int:program_id>', views.update_program, name="update_program"),
    path('plan_program.html', views.plan_program, name="plan_program"),
    path('courses.html', views.courses, name="courses"),
    path('course/<int:course_id>', views.course, name="course"),
    path('add_id_prefix', views.add_id_prefix, name="add_id_prefix"),
    path('display_prefixes', views.display_prefixes, name="display_prefixes"),
    path('add_ticket', views.add_ticket, name="add_ticket"),
    path('display_open_tickets', views.display_open_tickets, name="display_open_tickets"),
    path('display_closed_tickets', views.display_closed_tickets, name="display_closed_tickets"),
    path('display_ticket/<int:ticket_id>', views.display_ticket, name="display_ticket"),
    path('add_category.html', views.add_category, name="add_category"),
    path('display_categories.html', views.display_categories, name="display_categories"),
    path('clock.html', views.clock, name="clock"),
    path('manual_clock.html', views.manual_clock, name="manual_clock"),
    path('timesheet.html', views.timesheet, name="timesheet"),
    path('update_timesheet.html', views.update_timesheet, name="update_timesheet"),
    path('upload_timesheet.html', views.upload_timesheet, name="upload_timesheet"),
    path('onboard_client.html', views.onboard_client, name="onboard_client"),
    path('weekly_checklist/', views.weekly_checklist, name="weekly_checklist"),
    path('examination_mode/', views.examination_mode, name="examination_mode"),
    path('rating/<str:client>/<str:category>/<int:position>', views.rating, name="rating"),
       ]
