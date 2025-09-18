# Procfile (for Heroku-style deployment)
web: gunicorn app:app

# render.yaml (optional, for Render configuration)
services:
  - type: web
    name: ai-mood-dj
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: SPOTIPY_CLIENT_ID
        value: ede2e35b03b44094bf46a9bfba981a5d
      - key: SPOTIPY_CLIENT_SECRET  
        value: 05f17702932f4bf997fe6a312be031a2
      - key: SPOTIPY_REDIRECT_URI
        sync: false

# .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.cache
uploads/
*.log