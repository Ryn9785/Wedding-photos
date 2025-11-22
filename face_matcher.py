import face_recognition
import json
import sys
import numpy as np


def compare_faces(known_encoding_json, unknown_encoding_json, tolerance=0.6):
    """Compare face encodings and return similarity"""
    try:
        # Parse JSON encodings
        known_encoding = np.array(json.loads(known_encoding_json))
        unknown_encoding = np.array(json.loads(unknown_encoding_json))

        # Calculate face distance (lower = more similar)
        distance = face_recognition.face_distance(
            [known_encoding], unknown_encoding)[0]

        # Check if it's a match
        is_match = distance <= tolerance

        # Convert distance to confidence percentage (0.6 distance = 0% confidence, 0 = 100%)
        confidence = max(0, min(100, (1 - distance / 0.6) * 100))

        return {
            "success": True,
            "match": bool(is_match),
            "distance": float(distance),
            "confidence": float(confidence)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps(
            {"success": False, "error": "Need two face encodings"}))
        sys.exit(1)

    known_encoding = sys.argv[1]
    unknown_encoding = sys.argv[2]

    result = compare_faces(known_encoding, unknown_encoding)
    print(json.dumps(result))
