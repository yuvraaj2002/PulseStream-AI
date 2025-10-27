FROM python:3.10-slim

# Install system deps
RUN apt-get update && apt-get install -y gcc build-essential

WORKDIR /app

# Copy project
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
