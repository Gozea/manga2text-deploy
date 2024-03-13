# Use the official Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y tesseract-ocr libtesseract-dev ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*

# Copy the Flask application code to the working directory
COPY * ./

# Expose the port on which the Flask app will run
EXPOSE 5000

# Set the entry point command to run the Flask application
CMD ["python", "app.py"]
