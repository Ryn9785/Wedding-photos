# 💒 Wedding Photo Gallery

AI-powered wedding photo gallery with face recognition to find your photos instantly!

## Features

- 🎯 **AI Face Recognition** - Upload a selfie to find all photos with you
- 📸 **Beautiful Gallery** - Responsive grid layout with modal viewer
- 📱 **Mobile Friendly** - Works perfectly on phones and tablets
- ⬇️ **Download Photos** - Download individual photos or browse with arrows
- ☁️ **Cloud Storage** - Images hosted on Cloudinary

## Deployment Instructions

### Option 1: Deploy to Render (Recommended - Free)

1. **Create a GitHub account** (if you don't have one)
   - Go to https://github.com
   - Sign up for free

2. **Create a new GitHub repository**
   - Click "New repository"
   - Name it "wedding-photo-gallery"
   - Set to Public
   - Don't initialize with README
   - Click "Create repository"

3. **Push your code to GitHub**
   - Open PowerShell in this folder
   - Run these commands:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/wedding-photo-gallery.git
   git push -u origin main
   ```

4. **Deploy on Render**
   - Go to https://render.com
   - Sign up with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect settings from `render.yaml`
   - Add Environment Variables:
     - `CLOUDINARY_CLOUD_NAME` - Your Cloudinary cloud name
     - `CLOUDINARY_API_KEY` - Your Cloudinary API key
     - `CLOUDINARY_API_SECRET` - Your Cloudinary API secret
   - Click "Create Web Service"
   - Wait 10-15 minutes for deployment

5. **Your site will be live!**
   - URL: `https://wedding-photo-gallery-xxxx.onrender.com`
   - Free tier includes HTTPS automatically

### Option 2: Deploy to Railway (Alternative - Free)

1. Push code to GitHub (steps 1-3 above)
2. Go to https://railway.app
3. Sign up with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select your repository
6. Add environment variables
7. Deploy!

### Option 3: Deploy to Vercel (Requires Pro for Python)

Vercel's free tier doesn't support Python backend well. Use Render or Railway instead.

## Environment Variables Required

Create a `.env` file with:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Get these from https://cloudinary.com (free account)

## Local Development

```powershell
# Create virtual environment
py -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
py app.py
```

Open http://localhost:5000

## Tech Stack

- **Backend**: Flask (Python)
- **AI/ML**: DeepFace, TensorFlow
- **Frontend**: Vanilla JavaScript, CSS
- **Storage**: Cloudinary
- **Deployment**: Render/Railway

## Notes

- First deployment takes 10-15 minutes (installing TensorFlow)
- Free tier may sleep after 15 mins of inactivity
- Upload photos using `upload.py` script before deploying
- Face database is pre-generated (`faces_db.json`)

## Support

For issues, check:
- Render logs for errors
- Environment variables are set correctly
- `faces_db.json` exists in the repository
- Images are uploaded to Cloudinary

---

Made with ❤️ for your special day
