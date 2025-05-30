FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONPATH=/app

# Expose port (if your app uses a specific port)
EXPOSE 4000

# Run the application
# CMD ["python", "-m", "src.app","uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "4000"]
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "4000"]