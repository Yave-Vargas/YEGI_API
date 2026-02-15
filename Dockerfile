# Official Python base image
FROM python:3.11-slim

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Avoid buffering in logs
ENV PYTHONUNBUFFERED=1

# Working directory within the container
WORKDIR /app

# We copy requirements first (better cache)
COPY requirements.txt .

# We installed dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# We copied the entire project
COPY . .

# Port that FastAPI will use
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
