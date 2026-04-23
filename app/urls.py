from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('hod_login/', views.hod_login, name='hod_login'),
    path('hod_dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('enter_roll_no/', views.enter_roll_no, name='enter_roll_no'),
    path('view_student_details/<roll_no>/', views.view_student_details, name='view_student_details'),
    path('hod_logout/', views.hod_logout, name='hod_logout'),

    path('student_login/', views.student_login, name='student_login'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('view_academic_details/', views.view_academic_details, name='view_academic_details'),
    path('view_financial_details/', views.view_financial_details, name='view_financial_details'),
    path('view_library_status/', views.view_library_status, name='view_library_status'),
    path('view_disciplinary_status/', views.view_disciplinary_status, name='view_disciplinary_status'),
    path('student_logout/', views.student_logout, name='student_logout'),

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),

    path('manage_students/', views.manage_students, name='manage_students'),
    path('manage_academic/', views.manage_academic, name='manage_academic'),
    path('manage_attendance/', views.manage_attendance, name='manage_attendance'),
    path('manage_fees/', views.manage_fees, name='manage_fees'),
    path('manage_library/', views.manage_library, name='manage_library'),
    path('manage_disciplinary/', views.manage_disciplinary, name='manage_disciplinary'),

    path('search-student/', views.admin_search_student, name='admin_search_student'),
    path('student-details/<str:roll_no>/', views.admin_student_details, name='admin_student_details'),
    path('bulk-operations/', views.bulk_operations, name='bulk_operations'),

    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),

    # ⭐ NEW ANALYTICS
    path('analytics_portal/', views.analytics_portal, name='analytics_portal'),
    path("filter/top-performers/", views.filter_top_performers, name="filter_top_performers"),
    path("filter/low-attendance/", views.filter_low_attendance, name="filter_low_attendance"),
    path("filter/backlogs/", views.filter_backlogs, name="filter_backlogs"),
    path("filter/cgpa-risk/", views.filter_cgpa_risk, name="filter_cgpa_risk"),
    path("filter/behavior-rating/", views.filter_behavior_rating, name="filter_behavior_rating"),
    path("filter/partial-fee/", views.filter_partial_fee, name="filter_partial_fee"),
    path("filter/placed/", views.filter_placed, name="filter_placed"),
    path("filter/not-placed/", views.filter_not_placed, name="filter_not_placed"),
    path("filter/mock-low/", views.filter_mock_low, name="filter_mock_low"),
    path("filter/internship-not-done/", views.filter_internship_not_done, name="filter_internship_not_done"),

]
