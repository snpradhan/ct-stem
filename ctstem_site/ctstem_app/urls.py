from django.conf.urls import url

from . import views

app_name = 'ctstem'

urlpatterns = [
    path('', views.home, name='home'),
    path('curricula/<str:bucket>/', views.curricula, name='curricula'),
    path('curricula/<str:bucket>/<str:status>/', views.curricula, name='curricula'),
    path('curriculatiles/', views.curriculatiles, name='curriculatiles'),
    path('curriculum/<int:id>/overview/', views.curriculumOverview, name='curriculumOverview'),
    path('curriculum/<int:id>/overview/<int:page>/', views.curriculumOverview, name='curriculumOverview'),
    path('curriculum/new/overview/', views.curriculumOverview, name='newCurriculumOverview'),
    path('curriculum/<int:curriculum_id>/page/new/', views.curriculumStep, name='newCurriculumStep'),
    path('curriculum/<int:curriculum_id>/page/<int:id>/', views.curriculumStep, name='curriculumStep'),
    path('curriculum/<int:curriculum_id>/page/<int:id>/delete/', views.deleteStep, name='deleteStep'),
    path('curriculum/<int:curriculum_id>/page/<int:id>/copy/', views.copyStep, name='copyStep'),
    path('curriculum/<int:curriculum_id>/page/reorder/', views.reorderSteps, name='reorderSteps'),
    path('curriculum/bookmark/<int:id>/', views.bookmarkCurriculum, name='bookmarkCurriculum'),
    path('curriculum/removeBookmark/<int:id>/', views.removeBookmark, name='removeBookmark'),
    path('curriculum/delete/<int:id>/', views.deleteCurriculum, name='deleteCurriculum'),
    path('curriculum/preview/<int:id>/', views.previewCurriculum, name='previewCurriculum'),
    path('curriculum/preview/<int:id>/pem_code/<slug:pem_code>/', views.previewCurriculum, name='previewCurriculum'),
    path('curriculum/share/<int:id>/', views.shareCurriculum, name='shareCurriculum'),
    path('curriculum/preview/<int:id>/page/<int:step_order>/', views.previewCurriculumActivity, name='previewCurriculumActivity'),
    path('curriculum/preview/<int:id>/page/<int:step_order>/pem_code/<slug:pem_code>/', views.previewCurriculumActivity, name='previewCurriculumActivity'),
    path('curriculum/pdf/<int:id>/', views.pdfCurriculum, name='pdfCurriculum'),
    path('curriculum/copy/<int:id>/', views.copyCurriculum, name='copyCurriculum'),
    path('curriculum/copy/<int:id>/pem_code/<slug:pem_code>/', views.copyCurriculum, name='copyCurriculum'),
    path('curriculum/assignment/<int:id>/', views.assignCurriculum, name='assignCurriculum'),
    path('curriculum/underlying/<int:id>/', views.underlyingCurriculumTable, name='underlyingCurriculumTable'),
    path('curriculum/attachments/<int:id>/<slug:flag>/', views.downloadAttachments, name='downloadAttachments'),
    path('curriculum/restore/<int:id>/', views.restoreCurriculum, name='restoreCurriculum'),
    path('curriculum/is_assigned/ajax/<int:id>/', views.is_curriculum_assigned_ajax, name='is_curriculum_assigned_ajax'),
    path('publication/<int:id>/', views.publication, name='publication'),
    path('publication/delete/<int:id>/', views.deletePublication, name='deletePublication'),
    path('publication/new/', views.publication, name='newPublication'),
    path('research/', views.publications, name='publications'),
    path('jobs/', views.notimplemented, name='jobs'),
    path('events/', views.notimplemented, name='events'),
    path('team/', views.team, name='team'),
    path('teamMembers/', views.teamMembers, name='teamMembers'),
    path('teamMember/<int:id>/', views.teamMember, name='teamMember'),
    path('teamMember/new/', views.teamMember, name='newMember'),
    path('teacherSupport/', views.teacherSupport, name='teacherSupport'),
    path('request_training/', views.request_training, name='request_training'),
    path('training_requests/', views.training_requests, name='training_requests'),
    path('deleteMember/<int:id>/', views.deleteMember, name='deleteMember'),
    path('teamProfile/<int:id>/', views.teamProfile, name='teamProfile'),
    path('teamRoles/', views.teamRoles, name='teamRoles'),
    path('register/', views.register, name='register'),
    path('register/group/<slug:group_code>/<str:email>/', views.register, name='register'),
    path('register/group/<slug:group_code>/', views.register, name='register'),
    path('preregister/group/<slug:group_code>/', views.preregister, name='preregister'),
    path('generate_code/', views.generate_code, name='generate_code'),
    path('upload/users/', views.user_upload, name='user_upload'),
    path('login/', views.user_login, name='login'),
    path('login_redirect/', views.login_redirect, name='login_redirect'),
    path('login/<str:user_name>/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user/<int:id>/', views.userProfile, name='userProfile'),
    path('user/delete/<int:id>/<slug:validation_code>/', views.deleteUser, name='deleteTeacher'),
    path('user/delete/<int:id>/', views.deleteUser, name='deleteUser'),
    path('user/reset_password/<int:id>/', views.resetPassword, name='resetPassword'),
    path('student/remove/<int:group_id>/<int:student_id>', views.removeStudent, name='removeStudent'),
    path('student/add/<int:group_id>/<int:student_id>', views.addStudent, name='addStudent'),
    path('student/create/<int:group_id>/', views.createStudent, name='createStudent'),
    path('taxonomy/search/', views.searchTaxonomy, name='searchTaxonomy'),
    path('standard/delete/<int:id>/', views.deleteStandard, name='deleteStandard'),
    path('standard/new/', views.standard, name='newStandard'),
    path('standard/<int:id>/', views.standard, name='standard'),
    path('standards/', views.standards, name='standards'),
    path('categories/<int:standard_id>/', views.categories, name='categories'),
    path('subcategories/<int:category_id>/', views.subcategories, name='subcategories'),
    path('users/<slug:role>/', views.users, name='users'),
    path('students/search/', views.searchStudents, name='searchStudents'),
    path('teachers/search/', views.searchTeachers, name='searchTeachers'),
    path('collaborators/search/', views.searchCollaborators, name='searchCollaborators'),
    path('collaborators/<int:id>/', views.getCollaborators, name='getCollaborators'),
    path('question/new/', views.question, name='newQuestion'),
    path('question/<int:id>/', views.question, name='question'),
    path('questions/<slug:status>/', views.questions, name='questions'),
    path('question/search/', views.searchQuestion, name='searchQuestion'),
    path('question/copy/<int:id>/', views.copyQuestion, name='copyQuestion'),
    path('question/delete/<int:id>/', views.deleteQuestion, name='deleteQuestion'),
    path('response/<int:instance_id>/<int:response_id>/', views.questionResponse, name='questionResponse'),
    path('group/<int:id>/', views.group, name='group'),
    path('group/delete/<int:id>/', views.deleteGroup, name='deleteGroup'),
    path('group/inactivate/<int:id>/', views.inactivateGroup, name='inactivateGroup'),
    path('groups/<slug:status>/', views.groups, name='groups'),
    path('group/new/', views.group, name='newGroup'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignmenttiles/', views.assignmenttiles, name='assignmenttiles'),
    path('assignment/<int:assignment_id>/new/', views.assignment, name='startAssignment'),
    path('assignment/<int:assignment_id>/<int:instance_id>/<int:step_order>/', views.assignment, name='resumeAssignment'),
    path('assignment/unlock/<int:assignment_id>/<int:instance_id>/', views.unlockAssignment, name='unlockAssignment'),
    path('assignment/lock_on_completion/<int:assignment_id>/<int:flag>/', views.lock_on_completion, name='lock_on_completion'),
    path('assignment/realtime_feedback/<int:assignment_id>/<int:flag>/', views.realtime_feedback, name='realtime_feedback'),
    path('assignment/add/<int:curriculum_id>/<int:group_id>/', views.addAssignment, name='addAssignment'),
    path('assignment/delete/<int:assignment_id>/', views.deleteAssignment, name='deleteAssignment'),
    path('assignment/archive/<int:instance_id>/', views.archiveAssignment, name='archiveAssignment'),
    path('assignment/search/', views.searchAssignment, name='searchAssignment'),
    path('export_response/<int:assignment_id>/', views.export_response, name='export_group_response'),
    path('export_response/<int:assignment_id>/<int:student_id>/', views.export_response, name='export_student_response'),
    path('export_all_response/<int:curriculum_id>/', views.export_all_response, name='export_all_response'),
    path('export_question_response/<int:question_id>/', views.export_question_response, name='export_question_response'),
    path('dashboard/group/<int:id>/<str:curriculum_status>/', views.groupDashboard, name='groupDashboard'),
    path('dashboard/assignment/<int:id>/', views.assignmentDashboard, name='assignmentDashboard'),
    path('dashboard/group/<int:group_id>/curriculum/<int:curriculum_id>/<str:curriculum_status>/', views.groupCurriculumDashboard, name='groupCurriculumDashboard'),
    path('subjects/', views.subjects, name='subjects'),
    path('subject/<int:id>/', views.subject, name='subject'),
    path('subject/new/', views.subject, name='newSubject'),
    path('subject/delete/<int:id>/', views.deleteSubject, name='deleteSubject'),
    path('schools/', views.schools, name='schools'),
    path('school/<int:id>/', views.school, name='school'),
    path('school/new/', views.school, name='newSchool'),
    path('school/delete/<int:id>/', views.deleteSchool, name='deleteSchool'),
    path('check_session/', views.check_session, name='check_session'),
    path('feedback/<int:assignment_id>/<int:instance_id>/', views.feedback, name='feedback'),
    path('feedback/question_review/<int:assignment_id>/<int:curriculum_question_id>/', views.question_response_review, name='question_response_review'),
    path('iframe_state/<int:instance_id>/<slug:iframe_id>/', views.iframe_state, name='iframe_state'),
    path('consent/', views.consent, name='consent'),
    path('load_consent/', views.load_consent, name='load_consent'),
    path('validate/', views.validate, name='validate'),
    path('validate/<slug:username>/<slug:validation_code>/', views.validate, name='validate'),
    path('subaction/<int:action>/', views.subaction, name='subaction'),
    path('category/new/', views.research_category, name='newCategory'),
    path('category/<int:id>/', views.research_category, name='research_category'),
    path('category/delete/<int:id>/', views.deleteCategory, name='deleteCategory'),
    path('categories/', views.research_categories, name='categories'),
    path('terms/', views.terms, name='terms'),
    path('help/', views.help, name='help'),
    path('clear_cache/', views.clear_cache, name='clear_cache'),
    path('release_note/<int:id>/', views.releaseNote, name='releaseNote'),
    path('release_note/delete/<int:id>/', views.deleteReleaseNote, name='deleteReleaseNote'),
    path('release_note/new/', views.releaseNote, name='newReleaseNote'),
    path('release_notes/', views.releaseNotes, name='releaseNotes'),
    path('topic/<int:id>/', views.topic, name='topic'),
    path('topic/new/<slug:topic_type>/', views.topic, name='newTopic'),
    path('topic/delete/<int:id>/', views.deleteTopic, name='deleteTopic'),
    path('topic/<int:topic_id>/subtopic/<int:id>/', views.subTopic, name='subTopic'),
    path('topic/<int:topic_id>/subtopic/new/', views.subTopic, name='newSubTopic'),
    path('topic/<int:topic_id>/subtopic/delete/<int:id>/', views.deleteSubTopic, name='deleteSubTopic'),
    path('topics/<slug:topic_type>/', views.topics, name='topics'),

]
