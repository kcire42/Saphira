FROM python:3.11-slim

WORKDIR /app

# 1. Install system dependencies (build-essential includes gcc and g++)
# We use --no-install-recommends to avoid bloat and keep the image lightweight
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy only requirements first (optimizes Docker cache)
COPY requirements.txt .

# 3. Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code
COPY . .

CMD ["tail", "-f", "/dev/null"]