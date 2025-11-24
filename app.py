from flask import Flask, render_template, request, jsonify
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

UPLOAD_FOLDER = 'wedding_photos'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/photos')
def get_photos():
    try:
        photos = []
        next_cursor = None
        
        # Fetch all photos using pagination (Cloudinary limits to 500 per request)
        while True:
            if next_cursor:
                result = cloudinary.api.resources(
                    type='upload',
                    prefix=f'{UPLOAD_FOLDER}/',
                    max_results=500,
                    next_cursor=next_cursor
                )
            else:
                result = cloudinary.api.resources(
                    type='upload',
                    prefix=f'{UPLOAD_FOLDER}/',
                    max_results=500
                )

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
            
            # Check if there are more results
            next_cursor = result.get('next_cursor')
            if not next_cursor:
                break

        return jsonify({'success': True, 'photos': photos, 'total': len(photos)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Wedding Photo Gallery Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
