# ============================================================
# DOCKERFILE — What this file does:
# Imagine you're packing your app into a shipping container.
# This file is the packing list. Docker reads it top-to-bottom
# and builds a portable image that runs ANYWHERE.
# ============================================================

# STEP 1: Start FROM a base image.
# Think of this like choosing a pre-furnished apartment.
# python:3.11-slim = Python already installed, but nothing extra (keeps it small).
FROM python:3.11-slim

# STEP 2: Set the working directory INSIDE the container.
# Every command after this runs from /app.
# It's like doing: cd /app
WORKDIR /app

# STEP 3: Copy the requirements file first (before the rest of the code).
# WHY? Docker caches layers. If requirements don't change,
# Docker won't re-install packages on the next build — saves time!
COPY requirements.txt .

# STEP 4: Install Python packages listed in requirements.txt
# --no-cache-dir = don't store the download cache (keeps image smaller)
RUN pip install --no-cache-dir -r requirements.txt

# STEP 5: Copy the rest of your app code into the container
COPY . .

# STEP 6: Tell Docker which port our app listens on.
# This is documentation — it doesn't actually open the port.
# docker-compose (below) does the actual port mapping.
EXPOSE 5000

# STEP 7: The command to RUN when the container starts.
# gunicorn = a production-grade web server (better than Flask's built-in one)
# -w 2 = use 2 worker processes
# -b 0.0.0.0:5000 = listen on all network interfaces, port 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
