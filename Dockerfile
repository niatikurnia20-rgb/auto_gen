# Use Python 3.9 Slim (Lightweight)
FROM python:3.9-slim

# 1. Install System Dependencies (FFmpeg & ImageMagick are CRITICAL)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 2. Fix ImageMagick Policy (Allow text usage)
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

# 3. Set Working Directory
WORKDIR /app

# 4. Copy Requirements and Install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy App Code
COPY . .

# 6. Create Temp Folders
RUN mkdir -p static/videos temp

# 7. Command to Run the App (Using Gunicorn for production)
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app", "--timeout", "300"]