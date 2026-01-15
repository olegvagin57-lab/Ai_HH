FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies (Alpine использует apk, который требует меньше памяти)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    git \
    linux-headers

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with progress
RUN pip install --no-cache-dir --progress-bar=on -r requirements.txt

# Install parse_hh_data for development/testing (optional, can be skipped if not needed)
# Uncomment the line below to enable HH parser support
# RUN pip install --no-cache-dir git+https://github.com/arinaaageeva/parse_hh_data.git

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
