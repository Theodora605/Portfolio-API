FROM python:3.12-alpine

EXPOSE 5000

WORKDIR /app

RUN apk add build-base linux-headers libpq-dev

COPY requirements.txt .

RUN pip install uwsgi
RUN pip install -r requirements.txt

COPY . .

CMD ["uwsgi", "--ini", "/app/wsgi.ini"]