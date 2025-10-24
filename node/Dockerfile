FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ ./src

# This is the correct command to run the app as a module
CMD ["python", "-m", "src.app"]