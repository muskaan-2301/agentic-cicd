FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Gunicorn ke zariye app run karein jo Cloud Run ke PORT ko automatically bind kar leta hai
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 "wsgi:app"
