from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^curricula/(?P<curriculum_type>[\w-]+)/$', views.curricula, name='curricula'),
    url(r'^curricula/(?P<curriculum_type>[\w-]+)/(?P<bookmark>[\w-]+)/$', views.curricula, name='curricula'),
    url(r'^curriculum/new/$', views.curriculum, name='newCurriculum'),
    url(r'^curriculum/(?P<id>[\d]+)/$', views.curriculum, name='curriculum'),
    url(r'^curriculum/bookmark/(?P<id>[\d]+)/$', views.bookmarkCurriculum, name='bookmarkCurriculum'),
    url(r'^curriculum/removeBookmark/(?P<id>[\d]+)/$', views.removeBookmark, name='removeBookmark'),
    url(r'^curriculum/delete/(?P<id>[\d]+)/$', views.deleteCurriculum, name='deleteCurriculum'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/$', views.previewCurriculum, name='previewCurriculum'),
    url(r'^curriculum/preview/(?P<id>[\d]+)/(?P<step_order>[\d]+)/$', views.previewCurriculum, name='previewCurriculum'),
    url(r'^curriculum/pdf/(?P<id>[\d]+)/$', views.pdfCurriculum, name='pdfCurriculum'),
    url(r'^curriculum/copy/(?P<id>[\d]+)/$', views.copyCurriculum, name='copyCurriculum'),
    url(r'^curriculum/assignment/(?P<id>[\d]+)/$', views.assignCurriculum, name='assignCurriculum'),
    url(r'^curriculum/attachments/(?P<id>[\d]+)/$', views.downloadAttachments, name='downloadAttachments'),
    url(r'^publication/(?P<slug>[\w-]+)/$', views.publication, name='publication'),
    url(r'^publication/delete/(?P<slug>[\w-]+)/$', views.deletePublication, name='deletePublication'),
    url(r'^publication/new/$', views.publication, name='newPublication'),
    url(r'^research/$', views.publications, name='publications'),
    url(r'^jobs/$', views.notimplemented, name='jobs'),
    url(r'^events/$', views.notimplemented, name='events'),
    url(r'^team/$', views.team, name='team'),
    url(r'^teamMembers/$', views.teamMembers, name='teamMembers'),
    url(r'^teamMember/(?P<id>[\d]+)/$', views.teamMember, name='teamMember'),
    url(r'^teamMember/new/$', views.teamMember, name='newMember'),
    url(r'^training/$', views.training, name='training'),
    url(r'^request_training/$', views.request_training, name='request_training'),
    url(r'^training_requests/$', views.training_requests, name='training_requests'),
    url(r'^deleteMember/(?P<id>[\d]+)/$', views.deleteMember, name='deleteMember'),
    url(r'^teamProfile/(?P<id>[\d]+)/$', views.teamProfile, name='teamProfile'),
    url(r'^teamRoles/$', views.teamRoles, name='teamRoles'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/group/(?P<group_id>[\d]+)/$', views.register, name='register'),
    url(r'^generate_code/$', views.generate_code, name='generate_code'),
    url(r'^upload/users$', views.user_upload, name='user_upload'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<id>[\d]+)/$', views.userProfile, name='userProfile'),
    url(r'^user/delete/(?P<id>[\d]+)/$', views.deleteUser, name='deleteUser'),
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
    url(r'^question/new/$', views.question, name='newQuestion'),
    url(r'^question/(?P<id>[\d]+)/$', views.question, name='question'),
    url(r'^response/(?P<instance_id>[\d]+)/(?P<response_id>[\d]+)/$', views.questionResponse, name='questionResponse'),
    url(r'^group/(?P<id>[\d]+)/$', views.group, name='group'),
    url(r'^group/delete/(?P<id>[\d]+)/$', views.deleteGroup, name='deleteGroup'),
    url(r'^groups/$', views.groups, name='groups'),
    url(r'^group/new/$', views.group, name='newGroup'),
    url(r'^assignments/(?P<bucket>[\w-]+)/$', views.assignments, name='assignments'),
    url(r'^assignment/(?P<assignment_id>[\d]+)/new/$', views.assignment, name='startAssignment'),
    url(r'^assignment/(?P<assignment_id>[\d]+)/(?P<instance_id>[\d]+)/(?P<step_order>[\d]+)/$', views.assignment, name='resumeAssignment'),
    url(r'^assignment/archive/(?P<instance_id>[\d]+)/$', views.archiveAssignment, name='archiveAssignment'),
    url(r'^assignment/search/$', views.searchAssignment, name='searchAssignment'),
    url(r'^export_response/(?P<assignment_id>[\d]+)/$', views.export_response, name='export_group_response'),
    url(r'^export_response/(?P<assignment_id>[\d]+)/(?P<student_id>[\d]+)/$', views.export_response, name='export_student_response'),
    url(r'^export_all_response/(?P<curriculum_id>[\d]+)/$', views.export_all_response, name='export_all_response'),
    url(r'^dashboard/group/(?P<id>[\d]+)/$', views.groupDashboard, name='groupDashboard'),
    url(r'^dashboard/assignment/(?P<id>[\d]+)/$', views.assignmentDashboard, name='assignmentDashboard'),
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
    url(r'^consent/$', views.consent, name='consent'),
    url(r'^load_consent/$', views.load_consent, name='load_consent'),
    url(r'^validate/$', views.validate, name='validate'),
    url(r'^subaction/(?P<action>[\d]+)/$', views.subaction, name='subaction'),


]
