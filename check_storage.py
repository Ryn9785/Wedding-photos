import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print("=" * 60)
print("Cloudinary Storage Usage Report")
print("=" * 60)
print()

try:
    # Get usage statistics
    usage = cloudinary.api.usage()

    # Storage (in bytes)
    storage_used = usage.get('storage', {}).get('usage', 0)
    storage_limit = usage.get('storage', {}).get('limit', 0)

    # Convert to MB and GB
    storage_used_mb = storage_used / (1024 * 1024)
    storage_used_gb = storage_used / (1024 * 1024 * 1024)
    storage_limit_mb = storage_limit / (1024 * 1024)
    storage_limit_gb = storage_limit / (1024 * 1024 * 1024)

    # Calculate remaining
    storage_remaining = storage_limit - storage_used
    storage_remaining_mb = storage_remaining / (1024 * 1024)
    storage_remaining_gb = storage_remaining / (1024 * 1024 * 1024)

    # Calculate percentage
    storage_percent = (storage_used / storage_limit *
                       100) if storage_limit > 0 else 0

    print("📊 STORAGE:")
    print(f"  Used:      {storage_used_gb:.2f} GB ({storage_used_mb:.1f} MB)")
    print(
        f"  Limit:     {storage_limit_gb:.2f} GB ({storage_limit_mb:.1f} MB)")
    print(
        f"  Remaining: {storage_remaining_gb:.2f} GB ({storage_remaining_mb:.1f} MB)")
    print(f"  Usage:     {storage_percent:.1f}%")
    print()

    # Bandwidth
    bandwidth_used = usage.get('bandwidth', {}).get('usage', 0)
    bandwidth_limit = usage.get('bandwidth', {}).get('limit', 0)
    bandwidth_used_gb = bandwidth_used / (1024 * 1024 * 1024)
    bandwidth_limit_gb = bandwidth_limit / (1024 * 1024 * 1024)
    bandwidth_percent = (bandwidth_used / bandwidth_limit *
                         100) if bandwidth_limit > 0 else 0

    print("🌐 BANDWIDTH (Monthly):")
    print(f"  Used:      {bandwidth_used_gb:.2f} GB")
    print(f"  Limit:     {bandwidth_limit_gb:.2f} GB")
    print(f"  Usage:     {bandwidth_percent:.1f}%")
    print()

    # Resources count
    resources = usage.get('resources', 0)
    resources_limit = usage.get('max_image_resources', 0)

    print("📷 RESOURCES:")
    print(f"  Images:    {resources}")
    if resources_limit > 0:
        print(f"  Limit:     {resources_limit}")
        print(f"  Remaining: {resources_limit - resources}")
    print()

    # Transformations
    transformations = usage.get('transformations', {}).get('usage', 0)
    transformations_limit = usage.get('transformations', {}).get('limit', 0)

    if transformations_limit > 0:
        transformations_percent = (
            transformations / transformations_limit * 100)
        print("🔄 TRANSFORMATIONS (Monthly):")
        print(f"  Used:      {transformations:,}")
        print(f"  Limit:     {transformations_limit:,}")
        print(f"  Usage:     {transformations_percent:.1f}%")
        print()

    # Plan information
    plan = usage.get('plan', 'Unknown')
    print(f"💼 Plan: {plan}")
    print()

    # Check if running low on storage
    if storage_percent > 90:
        print("⚠️  WARNING: Storage is over 90% full!")
    elif storage_percent > 75:
        print("⚠️  NOTICE: Storage is over 75% full")
    else:
        print("✅ Storage usage is healthy")

    print()
    print("=" * 60)

except Exception as e:
    print(f"Error fetching usage data: {str(e)}")
    print("\nMake sure your Cloudinary credentials are correct in .env file")
