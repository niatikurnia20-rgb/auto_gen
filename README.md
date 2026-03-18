<div align="center">

# 🎥 ClipCore AI Video Generator
### Free Tier Edition

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange.svg)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
![MoviePy](https://img.shields.io/badge/MoviePy-Video_Engine-orange.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**A fully automated, full-stack Python application that generates faceless YouTube Shorts using 100% free APIs.**

*No paid subscriptions. No expensive tools. Just pure automation.*

[Features](#-features) • [Installation](#-local-installation) • [Deployment](#️-deployment) • [Troubleshooting](#️-troubleshooting)

---

</div>

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 💰 **Zero Cost** | Uses Google Gemini 2.0 Flash (Free Tier) and Pexels API |
| 🧠 **Smart Scripting** | Generates engaging, factual scripts (Intro → 3 Facts → Outro) |
| 🎬 **Real Stock Footage** | Fetches relevant video clips (not just static images) from Pexels |
| ✂️ **Auto-Editing** | Stitches clips, adds voiceovers (TTS), and handles transitions using MoviePy |
| ⚡ **Background Processing** | Uses threading so the web UI never freezes while rendering |
| ☁️ **Cloud Ready** | Includes a Dockerfile for easy deployment on Render.com (Free Tier) |
| 🧹 **Disk Safety** | Automatically cleans up old video files to prevent storage crashes |

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)

</div>

- **Backend:** Flask (Python)
- **AI Logic:** Google Gemini 2.0 Flash / Pro
- **Video Engine:** MoviePy (v1.0.3 stable) + FFmpeg
- **Media Source:** Pexels Video API
- **Audio:** gTTS (Google Text-to-Speech)
- **Deployment:** Docker + Gunicorn

---

## 📋 Prerequisites

Before you begin, get your free API keys:

| Service | Link | Purpose |
|---------|------|---------|
| 🤖 Google Gemini | [Get API Key](https://aistudio.google.com/app/apikey) | AI Script Generation |
| 🎥 Pexels | [Get API Key](https://www.pexels.com/api/) | Stock Video Footage |
| 🎞️ FFmpeg | [Download](https://ffmpeg.org/download.html) | Video Processing |

---

## 💻 Local Installation

Follow these steps to run the app on your computer.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/youtube-auto-gen.git
cd youtube-auto-gen
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

Create a file named `.env` in the root folder and add your keys:

```env
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxx
PEXELS_API_KEY=563492ad6f91700001000001xxxxxxxxxxxx
```

> ⚠️ **Note:** Do not wrap keys in quotes.

### 5️⃣ Install FFmpeg & ImageMagick (Crucial!)

<details>
<summary><b>Windows</b></summary>

1. Download [FFmpeg](https://ffmpeg.org/download.html) and add to Path
2. Install [ImageMagick](https://imagemagick.org/script/download.php)
   - ✅ Check "Install legacy utilities" during installation

</details>

<details>
<summary><b>Mac</b></summary>

```bash
brew install ffmpeg imagemagick
```

</details>

<details>
<summary><b>Linux</b></summary>

```bash
sudo apt install ffmpeg imagemagick
```

</details>

### 6️⃣ Run the App

```bash
python app.py
```

🎉 Open your browser at **http://localhost:5000**

---

## ☁️ Deployment (Render.com)

This project is configured for **Render's Free Tier**.

### Step-by-Step Guide

1. **Push to GitHub**
   - Upload your code to a GitHub repository

2. **Sign up for Render**
   - Go to [dashboard.render.com](https://dashboard.render.com)

3. **New Web Service**
   - Click **New +** → **Web Service**
   - Connect your GitHub repo

4. **Configuration**
   | Setting | Value |
   |---------|-------|
   | Runtime | `Docker` ⚠️ Important! |
   | Instance Type | `Free` |

5. **Environment Variables**
   - Go to the **"Environment"** tab in Render
   - Add your API keys:
     ```
     GEMINI_API_KEY=your_key_here
     PEXELS_API_KEY=your_key_here
     ```

6. **Deploy**
   - Click **"Create Web Service"**
   - Render will automatically install Python, FFmpeg, and ImageMagick using the included Dockerfile

---

## 📂 Project Structure

```
youtube-auto-gen/
├── 📁 modules/
│   ├── __init__.py          # Exports functions
│   ├── script_gen.py        # Gemini AI Logic
│   ├── media_fetch.py       # Pexels API Logic
│   ├── tts_gen.py           # Text-to-Speech
│   └── video_editor.py      # MoviePy Editing Logic
├── 📁 static/
│   ├── style.css            # Styling
│   ├── script.js            # Frontend Logic
│   └── 📁 videos/           # Generated output (Auto-cleaned)
├── 📁 templates/
│   └── index.html           # Dashboard
├── app.py                   # Main Flask Server
├── config.py                # Configuration Management
├── Dockerfile               # Deployment Instructions
├── requirements.txt         # Python Libraries
└── .env                     # API Keys (Local only)
```

---

## ⚠️ Troubleshooting

<details>
<summary><b>🔴 "MoviePy Error: ImageMagick binary not found"</b></summary>

- **Local:** You didn't install ImageMagick or didn't check "Install legacy utilities" during setup
- **Render:** This shouldn't happen; the Dockerfile fixes this automatically

</details>

<details>
<summary><b>🔴 "Gemini 429 Quota Exceeded"</b></summary>

- The app includes retry logic that switches between `gemini-2.5-flash`, `gemini-flash-latest`, and `gemini-pro`
- If all fail, wait 1 minute and try again

</details>

<details>
<summary><b>🔴 "Disk Full" on Render</b></summary>

- The app has an auto-cleanup function (`cleanup_old_files`) in `app.py`
- Automatically deletes videos older than 10 minutes

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🔧 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🎉 Open a Pull Request

---

## 📜 License

This project is open-source under the **MIT License**. Feel free to modify and use it for your own YouTube channel!

---

## 🌟 Show Your Support

If this project helped you, please give it a ⭐️!

---

<div align="center">

**Made with ❤️ for Content Creators by Prithwiraj Das**

<p align="center">

<a href="https://youtube.com/@official_coding_concepts">
<img src="https://img.shields.io/badge/YouTube-red?style=for-the-badge&logo=youtube&logoColor=white"/>
</a>

<a href="https://github.com/prithwiraj84">
<img src="https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github&logoColor=white"/>
</a>

</p>

</div>
