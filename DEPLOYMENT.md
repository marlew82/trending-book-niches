# Deployment Guide - Amazon Book Trends Analyzer

## 🚀 Deploy to Render.com (Free & Easy)

### Step 1: Push to GitHub

1. Go to https://github.com and sign in (or create an account)
2. Click the **"+"** in the top right → **"New repository"**
3. Name it: `amazon-book-trends`
4. Make it **Public**
5. Click **"Create repository"**

6. In your terminal (in the project folder):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/amazon-book-trends.git
   git push -u origin main
   ```

### Step 2: Deploy to Render

1. Go to https://render.com
2. Click **"Get Started"** (sign up with GitHub - it's free!)
3. Click **"New +"** → **"Web Service"**
4. Click **"Connect a repository"** → Find your `amazon-book-trends` repo
5. Click **"Connect"**

**Fill in these settings:**
- **Name**: `book-trends-analyzer` (or whatever you want)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && python build.py`
- **Start Command**: `gunicorn app:app`
- **Plan**: Select **"Free"**

6. Click **"Create Web Service"**

### Step 3: Wait for Deployment

- Render will build your app (takes 3-5 minutes)
- You'll see a green **"Live"** badge when ready
- Your URL will be something like: `https://book-trends-analyzer.onrender.com`

### Step 4: Access Your Site!

Click on the URL and your beautiful book trends website will be **LIVE** on the internet! 🎉

---

## 🌐 Alternative: Deploy to Railway.app

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your `amazon-book-trends` repository
5. Railway will auto-detect it's a Python app
6. Click **"Deploy"**

That's it! Railway gives you a live URL automatically.

---

## 🔧 Alternative: Deploy to PythonAnywhere

### Step 1: Create Account

1. Go to https://www.pythonanywhere.com
2. Click **"Pricing & signup"** → **"Create a Beginner account"** (free)

### Step 2: Upload Code

1. Click **"Files"** tab
2. Upload your project files or clone from GitHub:
   ```bash
   git clone https://github.com/YOUR-USERNAME/amazon-book-trends.git
   ```

### Step 3: Setup Web App

1. Click **"Web"** tab → **"Add a new web app"**
2. Choose **"Flask"**
3. Python version: **3.9**
4. Path: `/home/YOUR-USERNAME/amazon-book-trends`
5. Update the WSGI file to point to `app:app`

### Step 4: Install Requirements

1. Open a **Bash console**
2. Run:
   ```bash
   cd amazon-book-trends
   pip3 install -r requirements.txt
   python3 build.py
   ```

### Step 5: Reload & Visit

1. Click **"Reload"** on the Web tab
2. Visit your URL: `YOUR-USERNAME.pythonanywhere.com`

---

## ✅ What Happens on Deployment

1. **Database Auto-Created**: The `build.py` script generates sample data automatically
2. **Static Files Served**: CSS/JS served correctly
3. **API Endpoints Work**: All `/api/*` endpoints functional
4. **No Database Setup Needed**: SQLite database is built-in!

---

## 🎯 Recommended: Render.com

**Why Render?**
- ✅ Easiest deployment
- ✅ Free SSL (HTTPS)
- ✅ Auto-deploys on git push
- ✅ No credit card required
- ✅ Good free tier

**Free Tier Limits:**
- App sleeps after 15 mins of inactivity
- Wakes up when someone visits (takes 30 seconds)
- Perfect for demos and personal projects!

---

## 📊 After Deployment

Once live, you can:
- Share the URL with anyone
- Access from any device
- No local setup needed
- Works on mobile too!

**Example URLs:**
- Render: `https://book-trends-analyzer.onrender.com`
- Railway: `https://book-trends.up.railway.app`
- PythonAnywhere: `https://yourusername.pythonanywhere.com`

---

## 🔧 Troubleshooting

**Build fails?**
- Check the build logs in Render dashboard
- Make sure all files are committed to GitHub
- Verify `requirements.txt` has all dependencies

**App won't start?**
- Check that `gunicorn` is in `requirements.txt`
- Verify the start command: `gunicorn app:app`
- Check Render logs for errors

**No data showing?**
- SSH into the app or check logs
- Verify `build.py` ran successfully
- Check that `data/books.db` was created

---

🎉 **That's it! Your book trends analyzer will be live on the internet!**
