from django.conf.urls import url

from . import views

app_name = 'ctstem'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^curricula/(?P<bucket>[\w-]+)/$', views.curricula, name='curricula'),
    url(r'^curricula/(?P<bucket>[\w-]+)/(?P<status>[\w-]+)/$', views.curricula, name='curricula'),
    url(r'^curriculatiles/$', views.curriculatiles, name='curriculatiles'),
    url(r'^curriculum/new/$', views.curriculum, name='newCurriculum'),
    url(r'^curriculum/(?P<id>[\d]+)/$', views.curriculum, name='curriculum'),
    url(r'^curriculum/(?P<id>[\d]+)/overview/$', views.curriculumOverview, name='curriculumOverview'),
    url(r'^curriculum/(?P<id>[\d]+)/overview/(?P<page>[\d]+)/$', views.curriculumOverview, name='curriculumOverview'),
    url(r'^curriculum/new/overview/$', views.curriculumOverview, name='newCurriculumOverview'),
    url(r'^curriculum/(?P<curriculum_id>[\d]+)/page/new/$', views.curriculumStep, name='newCurriculumStep'),
    url(r'^curriculum/(?P<curriculum_id>[\d]+)/page/(?P<id>[\d]+)/$', views.curriculumStep, name='curriculumStep'),
    url(r'^curriculum/(?P<curriculum_id>[\d]+)/page/(?P<id>[\d]+)/delete/$', views.deleteStep, name='deleteStep'),
    url(r'^curriculum/(?P<curriculum_id>[\d]+)/page/(?P<id>[\d]+)/copy/$', views.copyStep, name='copyStep'),
    url(r'^curriculum/(?P<curriculum_id>[\d]+)/page/reorder/$', views.reorderSteps, name='reorderSteps'),
    url(r'^curriculum/bookmark/(?P<id>[\d]+)/$', views.bookmarkCurriculum, name='bookmarkCurriculum'),
    url(r'^curriculum/removeBookmark/(?P<id>[\d]+)/$', views.removeBookmark, name='removeBookmark'),
    url(r'^curriculum/delete/(?P<id>[\d]+)/$', views.deleteCurriculum, name='deleteCurriculum'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/$', views.previewCurriculum, name='previewCurriculum'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/pem_code/(?P<pem_code>[a-zA-Z0-9_]+)/$', views.previewCurriculum, name='previewCurriculum'),
    url(r'^curriculum/share/(?P<id>[\d]+)/$', views.shareCurriculum, name='shareCurriculum'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/page/(?P<step_order>[\d]+)/$', views.previewCurriculumActivity, name='previewCurriculumActivity'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/page/(?P<step_order>[\d]+)/pem_code/(?P<pem_code>[a-zA-Z0-9_]+)/$', views.previewCurriculumActivity, name='previewCurriculumActivity'),
    url(r'^curriculum/pdf/(?P<id>[\d]+)/$', views.pdfCurriculum, name='pdfCurriculum'),
    url(r'^curriculum/copy/(?P<id>[\d]+)/$', views.copyCurriculum, name='copyCurriculum'),
    url(r'^curriculum/copy/(?P<id>[\d]+)/pem_code/(?P<pem_code>[a-zA-Z0-9_]+)/$', views.copyCurriculum, name='copyCurriculum'),
    url(r'^curriculum/assignment/(?P<id>[\d]+)/$', views.assignCurriculum, name='assignCurriculum'),
    url(r'^curriculum/underlying/(?P<id>[\d]+)/$', views.underlyingCurriculumTable, name='underlyingCurriculumTable'),
    url(r'^curriculum/attachments/(?P<id>[\d]+)/(?P<flag>[a-zA-Z]+)$', views.downloadAttachments, name='downloadAttachments'),
    url(r'^curriculum/restore/(?P<id>[\d]+)/$', views.restoreCurriculum, name='restoreCurriculum'),
    url(r'^curriculum/is_assigned/ajax/(?P<id>[\d]+)/$', views.is_curriculum_assigned_ajax, name='is_curriculum_assigned_ajax'),
    url(r'^publication/(?P<id>[\d]+)/$', views.publication, name='publication'),
    url(r'^publication/delete/(?P<id>[\d]+)/$', views.deletePublication, name='deletePublication'),
    url(r'^publication/new/$', views.publication, name='newPublication'),
    url(r'^research/$', views.publications, name='publications'),
    url(r'^jobs/$', views.notimplemented, name='jobs'),
    url(r'^events/$', views.notimplemented, name='events'),
    url(r'^team/$', views.team, name='team'),
    url(r'^teamMembers/$', views.teamMembers, name='teamMembers'),
    url(r'^teamMember/(?P<id>[\d]+)/$', views.teamMember, name='teamMember'),
    url(r'^teamMember/new/$', views.teamMember, name='newMember'),
    url(r'^teacherSupport/$', views.teacherSupport, name='teacherSupport'),
    url(r'^request_training/$', views.request_training, name='request_training'),
    url(r'^training_requests/$', views.training_requests, name='training_requests'),
    url(r'^deleteMember/(?P<id>[\d]+)/$', views.deleteMember, name='deleteMember'),
    url(r'^teamProfile/(?P<id>[\d]+)/$', views.teamProfile, name='teamProfile'),
    url(r'^teamRoles/$', views.teamRoles, name='teamRoles'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/group/(?P<group_code>[a-zA-Z0-9_]+)/(?P<email>[A-Za-z0-9._\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,4})/$', views.register, name='register'),
    url(r'^register/group/(?P<group_code>[a-zA-Z0-9_]+)/$', views.register, name='register'),
    url(r'^preregister/group/(?P<group_code>[a-zA-Z0-9_]+)/$', views.preregister, name='preregister'),
    url(r'^generate_code/$', views.generate_code, name='generate_code'),
    url(r'^upload/users/$', views.user_upload, name='user_upload'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^login/(?P<user_name>[A-Za-z0-9._@+\-]+)/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<id>[\d]+)/$', views.userProfile, name='userProfile'),
    url(r'^user/delete/(?P<id>[\d]+)/(?P<validation_code>[a-zA-Z0-9_]+)/$', views.deleteUser, name='deleteTeacher'),
    url(r'^user/delete/(?P<id>[\d]+)/$', views.deleteUser, name='deleteUser'),
    url(r'^user/reset_password/(?P<id>[\d]+)/$', views.resetPassword, name='resetPassword'),
    url(r'^student/remove/(?P<group_id>[\d]+)/(?P<student_id>[\d]+)$', views.removeStudent, name='removeStudent'),
    url(r'^student/add/(?P<group_id>[\d]+)/(?P<student_id>[\d]+)$', views.addStudent, name='addStudent'),
    url(r'^student/create/(?P<group_id>[\d]+)/$', views.createStudent, name='createStudent'),
    url(r'^taxonomy/search/$', views.searchTaxonomy, name='searchTaxonomy'),
    url(r'^standard/delete/(?P<id>[\d]+)/$', views.deleteStandard, name='deleteStandard'),
    url(r'^standard/new/$', views.standard, name='newStandard'),
    url(r'^standard/(?P<id>[\d]+)/$', views.standard, name='standard'),
    url(r'^standards/$', views.standards, name='standards'),
    url(r'^categories/(?P<standard_id>[\d]+)/$', views.categories, name='categories'),
    url(r'^subcategories/(?P<category_id>[\d]+)/$', views.subcategories, name='subcategories'),
    url(r'^users/(?P<role>[a-zA-Z0-9_]+)/$', views.users, name='users'),
    url(r'^students/search/$', views.searchStudents, name='searchStudents'),
    url(r'^teachers/search/$', views.searchTeachers, name='searchTeachers'),
    url(r'^collaborators/search/$', views.searchCollaborators, name='searchCollaborators'),
    url(r'^collaborators/(?P<id>[\d]+)/$', views.getCollaborators, name='getCollaborators'),
    url(r'^question/new/$', views.question, name='newQuestion'),
    url(r'^question/(?P<id>[\d]+)/$', views.question, name='question'),
    url(r'^questions/(?P<status>[a-zA-Z0-9_]+)/$', views.questions, name='questions'),
    url(r'^question/search/$', views.searchQuestion, name='searchQuestion'),
    url(r'^question/copy/(?P<id>[\d]+)/$', views.copyQuestion, name='copyQuestion'),
    url(r'^question/delete/(?P<id>[\d]+)/$', views.deleteQuestion, name='deleteQuestion'),
    url(r'^response/(?P<instance_id>[\d]+)/(?P<response_id>[\d]+)/$', views.questionResponse, name='questionResponse'),
    url(r'^group/(?P<id>[\d]+)/$', views.group, name='group'),
    url(r'^group/delete/(?P<id>[\d]+)/$', views.deleteGroup, name='deleteGroup'),
    url(r'^group/inactivate/(?P<id>[\d]+)/$', views.inactivateGroup, name='inactivateGroup'),
    url(r'^groups/(?P<status>[a-zA-Z0-9_]+)/$', views.groups, name='groups'),
    url(r'^group/new/$', views.group, name='newGroup'),
    url(r'^assignments/(?P<bucket>[\w-]+)/$', views.assignments, name='assignments'),
    url(r'^assignment/(?P<assignment_id>[\d]+)/new/$', views.assignment, name='startAssignment'),
    url(r'^assignment/(?P<assignment_id>[\d]+)/(?P<instance_id>[\d]+)/(?P<step_order>[\d]+)/$', views.assignment, name='resumeAssignment'),
    url(r'^assignment/unlock/(?P<assignment_id>[\d]+)/(?P<instance_id>[\d]+)/$', views.unlockAssignment, name='unlockAssignment'),
    url(r'^assignment/lock_on_completion/(?P<assignment_id>[\d]+)/(?P<flag>[\d]+)/$', views.lock_on_completion, name='lock_on_completion'),
    url(r'^assignment/add/(?P<curriculum_id>[\d]+)/(?P<group_id>[\d]+)/$', views.addAssignment, name='addAssignment'),
    url(r'^assignment/delete/(?P<assignment_id>[\d]+)/$', views.deleteAssignment, name='deleteAssignment'),
    url(r'^assignment/archive/(?P<instance_id>[\d]+)/$', views.archiveAssignment, name='archiveAssignment'),
    url(r'^assignment/search/$', views.searchAssignment, name='searchAssignment'),
    url(r'^export_response/(?P<assignment_id>[\d]+)/$', views.export_response, name='export_group_response'),
    url(r'^export_response/(?P<assignment_id>[\d]+)/(?P<student_id>[\d]+)/$', views.export_response, name='export_student_response'),
    url(r'^export_all_response/(?P<curriculum_id>[\d]+)/$', views.export_all_response, name='export_all_response'),
    url(r'^export_question_response/(?P<question_id>[\d]+)/$', views.export_question_response, name='export_question_response'),
    url(r'^dashboard/group/(?P<id>[\d]+)/(?P<curriculum_status>[\w-]+)/$', views.groupDashboard, name='groupDashboard'),
    url(r'^dashboard/assignment/(?P<id>[\d]+)/$', views.assignmentDashboard, name='assignmentDashboard'),
    url(r'^dashboard/group/(?P<group_id>[\d]+)/curriculum/(?P<curriculum_id>[\d]+)/(?P<curriculum_status>[\w-]+)/$', views.groupCurriculumDashboard, name='groupCurriculumDashboard'),
    url(r'^subjects/$', views.subjects, name='subjects'),
    url(r'^subject/(?P<id>[\d]+)/$', views.subject, name='subject'),
    url(r'^subject/new/$', views.subject, name='newSubject'),
    url(r'^subject/delete/(?P<id>[\d]+)/$', views.deleteSubject, name='deleteSubject'),
    url(r'^schools/$', views.schools, name='schools'),
    url(r'^school/(?P<id>[\d]+)/$', views.school, name='school'),
    url(r'^school/new/$', views.school, name='newSchool'),
    url(r'^school/delete/(?P<id>[\d]+)/$', views.deleteSchool, name='deleteSchool'),
    url(r'^check_session/$', views.check_session, name='check_session'),
    url(r'^feedback/(?P<assignment_id>[\d]+)/(?P<instance_id>[\d]+)/$', views.feedback, name='feedback'),
    url(r'^feedback/question_review/(?P<assignment_id>[\d]+)/(?P<curriculum_question_id>[\d]+)/$', views.question_response_review, name='question_response_review'),
    url(r'^iframe_state/(?P<instance_id>[\d]+)/(?P<iframe_id>[a-zA-Z0-9_]+)/$', views.iframe_state, name='iframe_state'),
    url(r'^consent/$', views.consent, name='consent'),
    url(r'^load_consent/$', views.load_consent, name='load_consent'),
    url(r'^validate/$', views.validate, name='validate'),
    url(r'^validate/(?P<username>[a-zA-Z0-9_]+)/(?P<validation_code>[a-zA-Z0-9_]+)/$', views.validate, name='validate'),
    url(r'^subaction/(?P<action>[\d]+)/$', views.subaction, name='subaction'),
    url(r'^category/new/$', views.research_category, name='newCategory'),
    url(r'^category/(?P<id>[\d]+)/$', views.research_category, name='research_category'),
    url(r'^category/delete/(?P<id>[\d]+)/$', views.deleteCategory, name='deleteCategory'),
    url(r'^categories/$', views.research_categories, name='categories'),
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^help/$', views.help, name='help'),
    url(r'^clear_cache/$', views.clear_cache, name='clear_cache'),
    url(r'^release_note/(?P<id>[\d]+)/$', views.releaseNote, name='releaseNote'),
    url(r'^release_note/delete/(?P<id>[\d]+)/$', views.deleteReleaseNote, name='deleteReleaseNote'),
    url(r'^release_note/new/$', views.releaseNote, name='newReleaseNote'),
    url(r'^release_notes/$', views.releaseNotes, name='releaseNotes'),
    url(r'^topic/(?P<id>[\d]+)/$', views.topic, name='topic'),
    url(r'^topic/new/(?P<topic_type>[a-zA-Z0-9_]+)/$', views.topic, name='newTopic'),
    url(r'^topic/delete/(?P<id>[\d]+)/$', views.deleteTopic, name='deleteTopic'),
    url(r'^topic/(?P<topic_id>[\d]+)/subtopic/(?P<id>[\d]+)/$', views.subTopic, name='subTopic'),
    url(r'^topic/(?P<topic_id>[\d]+)/subtopic/new/$', views.subTopic, name='newSubTopic'),
    url(r'^topic/(?P<topic_id>[\d]+)/subtopic/delete/(?P<id>[\d]+)/$', views.deleteSubTopic, name='deleteSubTopic'),
    url(r'^topics/(?P<topic_type>[a-zA-Z0-9_]+)/$', views.topics, name='topics'),



]
