import json
import csv
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q
from .models import Student, AttendanceRecord
from .face_utils import encode_face_from_image, recognize_face_from_frame


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────
def dashboard(request):
    today = date.today()
    total_students = Student.objects.filter(is_active=True).count()
    today_present = AttendanceRecord.objects.filter(date=today, status='present').count()
    today_late = AttendanceRecord.objects.filter(date=today, status='late').count()
    today_absent = total_students - today_present - today_late

    # Last 7 days attendance chart data
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = AttendanceRecord.objects.filter(date=d, status__in=['present', 'late']).count()
        chart_labels.append(d.strftime('%d %b'))
        chart_data.append(count)

    recent_attendance = AttendanceRecord.objects.select_related('student').order_by('-date', '-time_in')[:10]

    context = {
        'total_students': total_students,
        'today_present': today_present,
        'today_late': today_late,
        'today_absent': today_absent if today_absent > 0 else 0,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_attendance': recent_attendance,
        'today': today,
    }
    return render(request, 'attendance_app/dashboard.html', context)


# ─────────────────────────────────────────
# STUDENTS
# ─────────────────────────────────────────
def student_list(request):
    students = Student.objects.filter(is_active=True).annotate(
        total_present=Count('attendance_records', filter=Q(attendance_records__status='present'))
    )
    return render(request, 'attendance_app/student_list.html', {'students': students})


def add_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        department = request.POST.get('department', '').strip()
        phone = request.POST.get('phone', '').strip()
        photo = request.FILES.get('photo')

        if not student_id or not name:
            messages.error(request, 'Student ID aur Naam zaroori hai!')
            return redirect('add_student')

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, f'Student ID {student_id} already exists!')
            return redirect('add_student')

        student = Student.objects.create(
            student_id=student_id,
            name=name,
            email=email,
            department=department,
            phone=phone,
            photo=photo,
        )

        # Face encoding generate karo agar photo upload ki ho
        if photo:
            photo.seek(0)
            encoding = encode_face_from_image(photo)
            if encoding:
                student.face_encoding = encoding
                student.save()
                messages.success(request, f'{name} register ho gaya! Face recognition ready hai.')
            else:
                messages.warning(request, f'{name} register ho gaya, lekin photo me face detect nahi hua.')
        else:
            messages.success(request, f'{name} register ho gaya! (Photo baad me add karo)')

        return redirect('student_list')

    departments = Student.objects.values_list('department', flat=True).distinct()
    return render(request, 'attendance_app/add_student.html', {'departments': departments})


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.is_active = False
        student.save()
        messages.success(request, f'{student.name} ko delete kar diya.')
    return redirect('student_list')


# ─────────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────────
def attendance_view(request):
    today = date.today()
    records = AttendanceRecord.objects.filter(date=today).select_related('student')
    students_with_attendance = Student.objects.filter(is_active=True)

    context = {
        'records': records,
        'students': students_with_attendance,
        'today': today,
        'total': students_with_attendance.count(),
        'present_count': records.filter(status='present').count(),
        'late_count': records.filter(status='late').count(),
    }
    return render(request, 'attendance_app/attendance.html', context)


@csrf_exempt
def mark_attendance(request):
    """Face recognition se attendance mark karo - API endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            frame_data = data.get('image')

            if not frame_data:
                return JsonResponse({'success': False, 'message': 'Image data nahi mili'})

            known_students = Student.objects.filter(is_active=True).exclude(face_encoding__isnull=True)

            if not known_students.exists():
                return JsonResponse({'success': False, 'message': 'Koi registered student nahi hai'})

            result = recognize_face_from_frame(frame_data, known_students)

            if result is None:
                return JsonResponse({'success': False, 'message': 'Koi face detect nahi hua'})

            if result.get('demo_mode'):
                return JsonResponse({'success': False, 'message': result['message']})

            student = result['student']
            confidence = result['confidence']
            today = date.today()
            now = datetime.now().time()

            # Already marked check
            existing = AttendanceRecord.objects.filter(student=student, date=today).first()
            if existing:
                return JsonResponse({
                    'success': False,
                    'message': f'{student.name} ki attendance aaj already mark ho chuki hai!',
                    'already_marked': True,
                    'student_name': student.name,
                    'student_id': student.student_id,
                })

            # Late check: 9:00 AM ke baad late
            status = 'late' if now.hour >= 9 else 'present'

            AttendanceRecord.objects.create(
                student=student,
                date=today,
                time_in=now,
                status=status,
                confidence=confidence,
                marked_by='face_recognition'
            )

            return JsonResponse({
                'success': True,
                'message': f'✅ {student.name} - Attendance Mark!',
                'student_name': student.name,
                'student_id': student.student_id,
                'department': student.department,
                'status': status,
                'confidence': confidence,
                'time': now.strftime('%I:%M %p'),
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def manual_attendance(request):
    """Manual attendance mark karo"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status', 'present')
        att_date = request.POST.get('date', str(date.today()))

        student = get_object_or_404(Student, student_id=student_id, is_active=True)
        att_date_obj = datetime.strptime(att_date, '%Y-%m-%d').date()

        record, created = AttendanceRecord.objects.get_or_create(
            student=student,
            date=att_date_obj,
            defaults={
                'time_in': datetime.now().time(),
                'status': status,
                'marked_by': 'manual',
                'confidence': 100.0,
            }
        )
        if not created:
            record.status = status
            record.marked_by = 'manual'
            record.save()
            messages.success(request, f'{student.name} ki attendance update kar di.')
        else:
            messages.success(request, f'{student.name} ki attendance mark kar di.')

        return redirect('attendance')

    students = Student.objects.filter(is_active=True)
    return render(request, 'attendance_app/manual_attendance.html', {'students': students})


# ─────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────
def reports(request):
    start_date = request.GET.get('start', str(date.today() - timedelta(days=30)))
    end_date = request.GET.get('end', str(date.today()))
    department = request.GET.get('department', '')

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start = date.today() - timedelta(days=30)
        end = date.today()

    records = AttendanceRecord.objects.filter(
        date__range=[start, end]
    ).select_related('student')

    if department:
        records = records.filter(student__department=department)

    # Student-wise summary
    students = Student.objects.filter(is_active=True)
    if department:
        students = students.filter(department=department)

    summary = []
    total_days = (end - start).days + 1
    for student in students:
        student_records = records.filter(student=student)
        present = student_records.filter(status__in=['present', 'late']).count()
        late = student_records.filter(status='late').count()
        percentage = round((present / total_days) * 100, 1) if total_days > 0 else 0
        summary.append({
            'student': student,
            'present': present,
            'late': late,
            'absent': total_days - present,
            'percentage': percentage,
        })

    departments = Student.objects.values_list('department', flat=True).distinct()

    context = {
        'summary': summary,
        'records': records.order_by('-date')[:50],
        'start_date': start_date,
        'end_date': end_date,
        'departments': departments,
        'selected_dept': department,
        'total_days': total_days,
    }
    return render(request, 'attendance_app/reports.html', context)


def export_csv(request):
    start_date = request.GET.get('start', str(date.today() - timedelta(days=30)))
    end_date = request.GET.get('end', str(date.today()))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Department', 'Date', 'Time In', 'Status', 'Confidence', 'Marked By'])

    records = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('student').order_by('date', 'student__name')

    for r in records:
        writer.writerow([
            r.student.student_id,
            r.student.name,
            r.student.department,
            r.date,
            r.time_in.strftime('%H:%M:%S') if r.time_in else '',
            r.get_status_display(),
            f"{r.confidence:.1f}%",
            r.marked_by,
        ])

    return response


@csrf_exempt
def recognize_face_api(request):
    """Simple API for testing face recognition"""
    if request.method == 'POST':
        return mark_attendance(request)
    return JsonResponse({'status': 'Face Recognition API ready'})
