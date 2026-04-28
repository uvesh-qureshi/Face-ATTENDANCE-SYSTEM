from django.contrib import admin
from .models import Student, AttendanceRecord

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'department', 'email', 'is_active', 'registered_at']
    list_filter = ['department', 'is_active']
    search_fields = ['student_id', 'name', 'email']
    readonly_fields = ['registered_at']

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'time_in', 'status', 'confidence']
    list_filter = ['status', 'date']
    search_fields = ['student__name', 'student__student_id']
    date_hierarchy = 'date'
