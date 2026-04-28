from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Student ID")
    name = models.CharField(max_length=100, verbose_name="Full Name")
    email = models.EmailField(blank=True, verbose_name="Email")
    department = models.CharField(max_length=100, blank=True, verbose_name="Department")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Phone")
    photo = models.ImageField(upload_to='faces/', blank=True, null=True, verbose_name="Photo")
    face_encoding = models.TextField(blank=True, null=True)
    registered_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

    class Meta:
        ordering = ['name']
        verbose_name = "Student"
        verbose_name_plural = "Students"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.CharField(max_length=50, default='face_recognition')
    confidence = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', '-time_in']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
