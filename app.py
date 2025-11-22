from flask import Flask, render_template, request, jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from deepface import DeepFace
import cv2
import numpy as np
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

UPLOAD_FOLDER = 'wedding_photos'
FACES_DB_FILE = 'faces_db.json'

# Load faces database
faces_database = []
if os.path.exists(FACES_DB_FILE):
    with open(FACES_DB_FILE, 'r') as f:
        faces_database = json.load(f)
    print(f"Loaded face data for {len(faces_database)} photos")
else:
    print("Warning: faces_db.json not found. Run upload script first.")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/photos')
def get_photos():
    try:
        result = cloudinary.api.resources(
            type='upload',
            prefix=f'{UPLOAD_FOLDER}/',
            max_results=500
        )

        photos = []
        for photo in result['resources']:
            photos.append({
                'publicId': photo['public_id'],
                'url': cloudinary.CloudinaryImage(photo['public_id']).build_url(
                    width=400, height=400, crop='fill', quality='auto', fetch_format='auto'
                ),
                'fullUrl': cloudinary.CloudinaryImage(photo['public_id']).build_url(
                    quality='auto', fetch_format='auto'
                )
            })

        return jsonify({'success': True, 'photos': photos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/face-match', methods=['POST'])
def face_match():
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'No photo uploaded'}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No photo selected'}), 400

        if len(faces_database) == 0:
            return jsonify({
                'success': False,
                'error': 'Face database not loaded. Please run upload script first.'
            }), 500

        # Read uploaded image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        user_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Save temporarily for DeepFace
        temp_selfie_path = 'temp_selfie.jpg'
        cv2.imwrite(temp_selfie_path, user_img)

        print("Analyzing uploaded selfie...")

        # Extract face embedding from selfie
        try:
            user_embedding = DeepFace.represent(
                img_path=temp_selfie_path,
                model_name='Facenet',
                enforce_detection=True
            )

            if not user_embedding or len(user_embedding) == 0:
                os.remove(temp_selfie_path)
                return jsonify({
                    'success': False,
                    'error': 'No face detected in uploaded photo. Please use a clear selfie.'
                })

            user_face_embedding = user_embedding[0]['embedding']

        except Exception as e:
            os.remove(temp_selfie_path)
            return jsonify({
                'success': False,
                'error': f'No face detected: {str(e)}'
            })

        print("Face detected, searching for matches...")

        # Find matching photos
        matched_photos = []

        for photo_data in faces_database:
            if 'embeddings' in photo_data and len(photo_data['embeddings']) > 0:
                # Check each face in the photo
                for face_embedding in photo_data['embeddings']:
                    # Calculate cosine similarity
                    distance = calculate_cosine_distance(
                        user_face_embedding, face_embedding)

                    # Threshold for match (lower distance = more similar)
                    if distance < 0.6:  # Typical threshold for Facenet
                        confidence = max(0, (1 - distance / 0.6) * 100)
                        matched_photos.append({
                            'publicId': f"{UPLOAD_FOLDER}/{photo_data['publicId']}",
                            'fileName': photo_data['fileName'],
                            'confidence': round(confidence, 1),
                            'distance': float(distance)
                        })
                        break  # Only add photo once

        # Sort by confidence
        matched_photos.sort(key=lambda x: x['confidence'], reverse=True)

        # Add Cloudinary URLs
        photos_with_urls = []
        for photo in matched_photos:
            photos_with_urls.append({
                'publicId': photo['publicId'],
                'fileName': photo['fileName'],
                'url': cloudinary.CloudinaryImage(photo['publicId']).build_url(
                    width=400, height=400, crop='fill', quality='auto', fetch_format='auto'
                ),
                'fullUrl': cloudinary.CloudinaryImage(photo['publicId']).build_url(
                    quality='auto', fetch_format='auto'
                ),
                'confidence': photo['confidence']
            })

        # Clean up temp file
        os.remove(temp_selfie_path)

        print(f"Found {len(photos_with_urls)} matching photos")

        return jsonify({
            'success': True,
            'matchedPhotos': photos_with_urls,
            'totalMatches': len(photos_with_urls)
        })

    except Exception as e:
        if os.path.exists('temp_selfie.jpg'):
            os.remove('temp_selfie.jpg')
        print(f"Error in face matching: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def calculate_cosine_distance(embedding1, embedding2):
    """Calculate cosine distance between two embeddings"""
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)

    # Normalize
    embedding1 = embedding1 / np.linalg.norm(embedding1)
    embedding2 = embedding2 / np.linalg.norm(embedding2)

    # Cosine similarity
    similarity = np.dot(embedding1, embedding2)

    # Convert to distance (0 = identical, 2 = opposite)
    distance = 1 - similarity

    return distance


if __name__ == '__main__':
    print("Starting Wedding Photo Gallery Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
