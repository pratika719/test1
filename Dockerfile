# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 7860

# Start the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
