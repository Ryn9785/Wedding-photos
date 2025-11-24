import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
from pathlib import Path
from PIL import Image
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import argparse

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Configuration
USB_DRIVE = 'D:\\'  # USB drive path
UPLOAD_FOLDER = 'wedding_photos'
TARGET_SIZE = (2400, 2400)  # Max dimensions
UPLOADED_FILES = 'uploaded_files.txt'  # Track uploaded files
MAX_WORKERS = 5  # Increased for faster uploads
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Image extensions to look for
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

# Thread-safe data structures
uploaded_lock = threading.Lock()
stats_lock = threading.Lock()


def compress_image(image_path, quality=85):
    """Compress image to reduce file size"""
    img = Image.open(image_path)

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Resize if too large
    img.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)

    # Save to bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)

    return buffer


def load_uploaded_files():
    """Load list of already uploaded files"""
    if os.path.exists(UPLOADED_FILES):
        with open(UPLOADED_FILES, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def mark_as_uploaded(file_name):
    """Mark a file as uploaded"""
    with uploaded_lock:
        with open(UPLOADED_FILES, 'a') as f:
            f.write(f"{file_name}\n")


def find_all_images(root_path):
    """Recursively find all image files in the directory tree"""
    print(f"Scanning {root_path} for images...")
    image_files = []
    
    # Walk through all directories recursively
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if Path(file).suffix in IMAGE_EXTENSIONS:
                full_path = Path(root) / file
                image_files.append(full_path)
    
    return image_files


def process_single_image(image_file, index, total):
    """Process a single image - compress and upload (NO face detection)"""
    file_name = image_file.name

    for attempt in range(MAX_RETRIES):
        try:
            print(f"[{index}/{total}] Processing: {file_name}")

            # Get original file size
            original_size = image_file.stat().st_size / (1024 * 1024)  # MB

            # Compress image
            compressed_buffer = compress_image(str(image_file))
            compressed_size = compressed_buffer.getbuffer().nbytes / (1024 * 1024)
            print(f"  ↳ Compressed: {original_size:.2f}MB → {compressed_size:.2f}MB")

            # Upload to Cloudinary with retry
            result = cloudinary.uploader.upload(
                compressed_buffer,
                folder=UPLOAD_FOLDER,
                public_id=Path(file_name).stem,
                resource_type='image',
                quality='auto:good',
                timeout=60
            )

            print(f"  ✓ Uploaded: {file_name}")
            mark_as_uploaded(file_name)

            return {'success': True, 'file_name': file_name}

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠ Retry {attempt + 1}/{MAX_RETRIES}: {file_name}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ✗ Failed after {MAX_RETRIES} attempts: {file_name} - {str(e)}")
                return {'success': False, 'error': str(e), 'file_name': file_name}


def upload_images_from_usb():
    print("=" * 70)
    print("USB Drive Wedding Photo Upload - FAST MODE (No Face Detection)")
    print("=" * 70)
    print()

    # Check if USB drive exists
    if not os.path.exists(USB_DRIVE):
        print(f"Error: USB drive {USB_DRIVE} not found!")
        return

    # Find all images recursively
    print(f"Scanning USB drive: {USB_DRIVE}")
    image_files = find_all_images(USB_DRIVE)

    if len(image_files) == 0:
        print(f"No images found in {USB_DRIVE}!")
        return

    print(f"Found {len(image_files)} image files across all folders")
    print()

    # Load existing progress
    uploaded_files = load_uploaded_files()
    remaining_files = [f for f in image_files if f.name not in uploaded_files]

    print(f"Total images found: {len(image_files)}")
    print(f"Already uploaded: {len(uploaded_files)}")
    print(f"Remaining: {len(remaining_files)}")
    print(f"Using {MAX_WORKERS} parallel workers")
    print()

    if len(remaining_files) == 0:
        print("All images already uploaded!")
        return

    # Show sample of folders being processed
    unique_dirs = set(str(f.parent) for f in remaining_files)
    print(f"Processing images from {len(unique_dirs)} different folders")
    sample_dirs = list(unique_dirs)[:5]
    for d in sample_dirs:
        print(f"  • {d}")
    if len(unique_dirs) > 5:
        print(f"  ... and {len(unique_dirs) - 5} more folders")
    print()
    print("NOTE: Face detection is DISABLED for faster uploads.")
    print("      You can run face detection separately later if needed.")
    print()

    success_count = 0
    error_count = 0
    start_time = time.time()

    # Process images in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single_image, img, i + 1, len(remaining_files)): img
            for i, img in enumerate(remaining_files)
        }

        # Process completed tasks
        for future in as_completed(future_to_file):
            try:
                result = future.result(timeout=120)
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"  ✗ Task failed: {str(e)}")
                error_count += 1

    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print()
    print("=" * 70)
    print("Upload Complete!")
    print("=" * 70)
    print(f"✓ Successfully uploaded (this session): {success_count}")
    print(f"✗ Failed: {error_count}")
    print(f"📊 Total uploaded: {len(uploaded_files) + success_count}/{len(image_files)}")
    print(f"⏱ Time taken: {minutes}m {seconds}s")
    if success_count > 0:
        avg_time = elapsed_time / success_count
        print(f"📈 Average: {avg_time:.1f}s per image")
    print()
    if error_count > 0 or len(uploaded_files) + success_count < len(image_files):
        print("⚠ Some images failed. Run the script again to retry.")
    print()
    print("All photos from USB drive have been processed!")
    print("Run 'python app.py' to start the web server!")


if __name__ == '__main__':
    upload_images_from_usb()
