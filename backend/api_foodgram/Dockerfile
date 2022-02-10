FROM python:3.8.5

WORKDIR /backend/api_foodgram
COPY . .
RUN pip install -r requirements.txt
CMD gunicorn api_foodgram.wsgi:application --bind 0.0.0.0:8000 