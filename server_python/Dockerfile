# server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

# Use python-dotenv to load environment variables
RUN pip install python-dotenv

# Run the app directly with Python and enable debug mode
CMD ["python", "app.py"]