# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 5001

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "blockchain_servir.app:create_app()"]
