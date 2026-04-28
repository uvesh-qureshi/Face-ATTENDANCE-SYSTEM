# 👁️ Face Recognition Attendance System

Django + OpenCV + face_recognition se bana hua smart attendance system.

## 🚀 Setup & Run

### 1. Python Virtual Environment banao
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Dependencies install karo
```bash
pip install -r requirements.txt
```

> ⚠️ **face_recognition install karne ke liye pehle dlib chahiye:**
> ```bash
> # Ubuntu/Debian:
> sudo apt-get install cmake libopenblas-dev liblapack-dev
> pip install dlib

> pip install face_recognition
>
> # Windows (easy way):
> pip install cmake
> pip install dlib
> pip install face_recognition
> ```

### 3. Database setup karo
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Server run karo
```bash
python manage.py runserver
```

### 5. Browser me kholo
```
http://127.0.0.1:8000/
```

---

## 📁 Project Structure
```
face_attendance/
├── face_attendance_project/     # Django settings
│   ├── settings.py
│   └── urls.py
├── attendance_app/              # Main app
│   ├── models.py               # Student, AttendanceRecord
│   ├── views.py                # All views & API
│   ├── urls.py                 # URL routing
│   ├── face_utils.py           # Face recognition logic
│   ├── admin.py                # Django admin config
│   └── templates/              # HTML templates
├── media/                       # Uploaded photos
├── requirements.txt
└── manage.py
```

## 🎯 Features

| Feature | Detail |
|---------|--------|
| 📸 Face Recognition | Real-time webcam attendance |
| 👥 Student Management | Add/Delete students with photo |
| ✏️ Manual Attendance | Backup manual entry |
| 📊 Dashboard | Live stats + charts |
| 📋 Reports | Student-wise attendance % |
| ⬇️ CSV Export | Date-range export |
| ⚙️ Admin Panel | /admin/ se full control |

## 🔗 URLs

| URL | Page |
|-----|------|
| `/` | Dashboard |
| `/attendance/` | Face Scan |
| `/students/` | Student List |
| `/students/add/` | Add Student |
| `/attendance/manual/` | Manual Attendance |
| `/reports/` | Reports |
| `/admin/` | Admin Panel |

## ⚙️ Late Time Change Karna
`views.py` me `mark_attendance()` function me:
```python
status = 'late' if now.hour >= 9 else 'present'
#                           ↑ yahan time badlo (24hr format)
```

## 👨‍💻 Tech Stack
- **Backend:** Django 4.2
- **Face Recognition:** face_recognition (dlib)
- **Camera:** OpenCV + Browser WebRTC
- **Database:** SQLite (production me PostgreSQL use karo)
- **Frontend:** HTML/CSS/JS (no framework)
