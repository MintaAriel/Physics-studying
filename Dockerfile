# Use slim Python image
FROM python:3.11-slim

# Prevent python buffering
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies (for PIL + PDFs if needed)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    gradio \
    pillow \
    pymupdf \
    sqlite3

# Expose Gradio port
EXPOSE 7860

# Run the app
CMD ["python", "scripts/get_exercises.py"]
