FROM python:3.9.5
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r ./requirements.txt
COPY . .
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000