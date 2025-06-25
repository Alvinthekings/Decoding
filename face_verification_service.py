from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import base64
import cv2
import mysql.connector

app = Flask(__name__)

# Connect to MySQL
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='studentmanagement'
)
cursor = db.cursor()

def load_known_faces():
    known_encodings = []
    known_names = []
    known_lrns = []
    known_grades = []

    cursor.execute("SELECT fullname, lrn, grade, face_encoding FROM student_faces")
    for fullname, lrn, grade, encoding_blob in cursor.fetchall():
        encoding = np.frombuffer(encoding_blob, dtype=np.float64)
        known_encodings.append(encoding)
        known_names.append(fullname)
        known_lrns.append(lrn)
        known_grades.append(grade)

    return known_encodings, known_names, known_lrns, known_grades

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    try:
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({'error': f'Failed to decode image: {str(e)}'}), 500

    unknown_encodings = face_recognition.face_encodings(img)
    if not unknown_encodings:
        return jsonify({'matched': False, 'message': 'No face detected'}), 200

    known_encodings, known_names, known_lrns, known_grades = load_known_faces()

    matches = face_recognition.compare_faces(known_encodings, unknown_encodings[0])
    if True in matches:
        index = matches.index(True)
        return jsonify({
            'matched': True,
            'fullname': known_names[index],
            'lrn': known_lrns[index],
            'grade': known_grades[index]
        })

    return jsonify({'matched': False, 'message': 'Face not recognized'}), 200

@app.route('/register_face', methods=['POST'])
def register_face():
    data = request.get_json()
    if not all(k in data for k in ('image', 'fullname', 'lrn', 'grade')):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    try:
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        encodings = face_recognition.face_encodings(img)
        if not encodings:
            return jsonify({'success': False, 'message': 'No face detected'})

        encoding_blob = encodings[0].astype(np.float64).tobytes()

        cursor.execute("""
            INSERT INTO student_faces (fullname, lrn, grade, face_encoding)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            fullname = VALUES(fullname),
            grade = VALUES(grade),
            face_encoding = VALUES(face_encoding)
        """, (data['fullname'], data['lrn'], data['grade'], encoding_blob))
        db.commit()

        return jsonify({'success': True, 'message': 'Face registered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
