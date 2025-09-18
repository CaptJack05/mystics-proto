from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
import random
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from deepface import DeepFace

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Spotify setup
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "ede2e35b03b44094bf46a9bfba981a5d")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "05f17702932f4bf997fe6a312be031a2")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:5000/callback")

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state",
    cache_path=".cache"
))

# Emoji map for emotions
EMOJI_MAP = {
    "happy": "😄",
    "sad": "😢", 
    "angry": "😠",
    "surprise": "😲",
    "fear": "😨",
    "neutral": "😐"
}

def detect_emotion(image_array):
    """Detect emotion from image array"""
    try:
        result = DeepFace.analyze(
            image_array, 
            actions=['emotion'], 
            enforce_detection=False
        )
        return result[0]['dominant_emotion']
    except Exception as e:
        print(f"Error detecting emotion: {e}")
        return "neutral"

def generate_music(emotion):
    """Generate music based on emotion"""
    mood_map = {
        "happy": "happy upbeat pop",
        "sad": "sad emotional songs",
        "angry": "heavy rock metal",
        "surprise": "edm electronic dance",
        "fear": "dark ambient horror",
        "neutral": "chill lofi relaxing"
    }
    
    query = mood_map.get(emotion.lower(), "chill music")
    
    try:
        results = sp.search(q=query, type="track", limit=20)
        
        if results["tracks"]["items"]:
            track = random.choice(results["tracks"]["items"])
            music_data = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"],
                "url": track["external_urls"]["spotify"],
                "image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                "preview_url": track.get("preview_url")
            }
            return music_data
        else:
            return None
    except Exception as e:
        print(f"Error generating music: {e}")
        return None

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_emotion():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Read and process image
        image_bytes = file.read()
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to OpenCV format
        image_array = np.array(image)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect emotion
        emotion = detect_emotion(image_array)
        emoji = EMOJI_MAP.get(emotion.lower(), "😐")
        
        # Generate music
        music_data = generate_music(emotion)
        
        # Convert image to base64 for display
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'emotion': emotion,
            'emoji': emoji,
            'music': music_data,
            'image': f"data:image/jpeg;base64,{img_str}"
        })
        
    except Exception as e:
        print(f"Error in analyze_emotion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/callback')
def spotify_callback():
    """Handle Spotify OAuth callback"""
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)