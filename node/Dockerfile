# node/Dockerfile

FROM python:3.10-slim

# 1. Install system dependencies needed for plyvel
#    - build-essential: provides C/C++ compilers and tools
#    - libleveldb-dev: provides the LevelDB library and header files
RUN apt-get update && apt-get install -y \
    build-essential \
    libleveldb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Now that libleveldb-dev is installed, this next command will succeed
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]