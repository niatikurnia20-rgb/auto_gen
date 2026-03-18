from flask import Flask, render_template, request, jsonify
import threading
import uuid
import os
import time

# Config Imports
from config import OUTPUT_FOLDER, TEMP_FOLDER

# Logic Imports
# Ensure your modules/__init__.py exports these correctly
from modules.script_gen import generate_script
from modules.tts_gen import generate_audio
from modules.media_fetch import fetch_stock_media
from modules.video_editor import create_video

app = Flask(__name__)

# In-memory storage for task status
# Note: In a paid app, use Redis/Database. For free tier, this works fine.
tasks = {}

def cleanup_old_files():
    """
    Deletes files in 'static/videos' and 'temp' older than 10 minutes.
    Essential for Render Free Tier to prevent disk full errors.
    """
    limit_age = 600  # 10 minutes in seconds
    now = time.time()

    folders = [OUTPUT_FOLDER, TEMP_FOLDER]
    
    for folder in folders:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                # Check if it's a file and older than limit
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > limit_age:
                        os.remove(file_path)
                        print(f"🗑️ Cleaned up old file: {filename}")
            except Exception as e:
                print(f"Cleanup Error {filename}: {e}")

def process_video_task(task_id, topic):
    """
    Background worker that runs the full video generation pipeline.
    """
    try:
        # 1. Script Generation (Gemini 2.0)
        tasks[task_id]['status'] = 'Writing Script...'
        script = generate_script(topic)
        tasks[task_id]['logs'].append(f"Script generated ({len(script.split())} words).")
        
        # 2. Audio Generation (TTS)
        tasks[task_id]['status'] = 'Recording Audio...'
        audio_filename = f"{task_id}.mp3"
        audio_path = os.path.join(TEMP_FOLDER, audio_filename)
        
        generate_audio(script, audio_path)
        tasks[task_id]['logs'].append("Audio recording ready.")

        # 3. Media Fetching (Video Clips)
        tasks[task_id]['status'] = 'Finding Stock Footage...'
        # Request 15 clips to cover a ~60s video
        media_files = fetch_stock_media(topic, count=15)
        
        if not media_files:
            raise Exception("No video clips found for this topic.")
            
        tasks[task_id]['logs'].append(f"Found {len(media_files)} video clips.")

        # 4. Video Rendering (MoviePy)
        tasks[task_id]['status'] = 'Rendering Final Video (This takes time)...'
        video_filename = f"{task_id}.mp4"
        video_path = os.path.join(OUTPUT_FOLDER, video_filename)
        
        # Create the video
        create_video(script, audio_path, media_files, video_path)
        
        # 5. Success
        tasks[task_id]['status'] = 'Completed'
        tasks[task_id]['video_url'] = f"/static/videos/{video_filename}"
        tasks[task_id]['logs'].append("Video Ready! Click Download.")

    except Exception as e:
        print(f"Task {task_id} Failed: {e}")
        tasks[task_id]['status'] = 'Failed'
        tasks[task_id]['logs'].append(f"Error: {str(e)}")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # 1. Run Cleanup First (Protect Server Storage)
    cleanup_old_files()

    data = request.json
    topic = data.get('topic')
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    # Create Job ID
    task_id = str(uuid.uuid4())
    
    # Initialize Status
    tasks[task_id] = {
        'status': 'Queued',
        'logs': ['Job started...'],
        'video_url': None
    }
    
    # Start Background Thread
    thread = threading.Thread(target=process_video_task, args=(task_id, topic))
    thread.daemon = True # Ensures thread dies if app restarts
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>')
def status(task_id):
    # Frontend polls this to update the progress bar
    return jsonify(tasks.get(task_id, {'status': 'Unknown', 'logs': []}))

if __name__ == '__main__':
    # Ensure folders exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    
    # ⚠️ CRITICAL FOR RENDER: Use PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    
    print(f"🚀 Server running at http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
