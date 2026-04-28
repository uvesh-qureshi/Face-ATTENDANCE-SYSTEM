from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/manual/', views.manual_attendance, name='manual_attendance'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_csv, name='export_csv'),
    path('api/recognize/', views.recognize_face_api, name='recognize_face_api'),
]
