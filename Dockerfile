# === Base Image ===
FROM python:3.10-slim

# === Environment Configuration ===
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# === Working Directory ===
WORKDIR /src

# === Install Dependencies ===
# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Copy Project Source ===
COPY ./app ./app

# === Expose Output Port ===
EXPOSE 8000

# === Application Entry Point ===
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
