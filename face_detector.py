import face_recognition
import json
import sys
from pathlib import Path


def analyze_image(image_path):
    """Detect faces and generate face encodings"""
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)

        # Get face encodings (128-dimensional vectors)
        face_encodings = face_recognition.face_encodings(image)

        if len(face_encodings) == 0:
            return {"success": False, "faces": 0}

        # Convert numpy arrays to lists for JSON serialization
        encodings_list = [encoding.tolist() for encoding in face_encodings]

        return {
            "success": True,
            "faces": len(face_encodings),
            "encodings": encodings_list
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps(
            {"success": False, "error": "No image path provided"}))
        sys.exit(1)

    image_path = sys.argv[1]
    result = analyze_image(image_path)
    print(json.dumps(result))
