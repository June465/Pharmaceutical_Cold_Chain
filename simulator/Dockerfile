# simulator/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The command to run the application
CMD ["python", "app.py"]