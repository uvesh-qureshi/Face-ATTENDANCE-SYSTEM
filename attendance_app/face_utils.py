"""
Face Recognition Utility Module
Uses: OpenCV + face_recognition library
Install: pip install face_recognition opencv-python
"""
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image

def encode_face_from_image(image_file):
    """
    Student ki photo se face encoding extract karo.
    Returns: JSON string of face encoding, or None if no face found.
    """
    try:
        import face_recognition
        img = Image.open(image_file).convert('RGB')
        img_array = np.array(img)
        encodings = face_recognition.face_encodings(img_array)
        if encodings:
            return json.dumps(encodings[0].tolist())
        return None
    except ImportError:
        # face_recognition not installed - return dummy encoding for demo
        return json.dumps([0.0] * 128)
    except Exception as e:
        print(f"Face encoding error: {e}")
        return None


def recognize_face_from_frame(frame_data, known_students):
    """
    Webcam frame se face recognize karo registered students me se.
    
    Args:
        frame_data: Base64 encoded image from webcam
        known_students: QuerySet of Student objects with face_encoding
    
    Returns:
        dict with student info and confidence, or None
    """
    try:
        import face_recognition

        # Decode base64 image
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        img_bytes = base64.b64decode(frame_data)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        frame_array = np.array(img)

        # Detect faces in frame
        face_locations = face_recognition.face_locations(frame_array)
        if not face_locations:
            return None

        face_encodings = face_recognition.face_encodings(frame_array, face_locations)
        if not face_encodings:
            return None

        unknown_encoding = face_encodings[0]

        # Compare with all registered students
        best_match = None
        best_distance = 1.0  # Lower is better, threshold = 0.6

        for student in known_students:
            if not student.face_encoding:
                continue
            known_encoding = np.array(json.loads(student.face_encoding))
            distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            if distance < best_distance and distance < 0.6:
                best_distance = distance
                best_match = student

        if best_match:
            confidence = round((1 - best_distance) * 100, 2)
            return {
                'student': best_match,
                'confidence': confidence,
                'distance': best_distance
            }
        return None

    except ImportError:
        # Demo mode - face_recognition not installed
        return {'demo_mode': True, 'message': 'Install face_recognition for real recognition'}
    except Exception as e:
        print(f"Recognition error: {e}")
        return None
