FROM python:3.6.1-alpine

RUN apk update \
  && apk add \
    build-base \
    libpq \
    zlib-dev \
    jpeg-dev

RUN mkdir /usr/src/app
RUN mkdir /ssl

WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir static
ENV PYTHONUNBUFFERED 1
ENV LIBRARY_PATH=/lib:/usr/lib

COPY . .

ENTRYPOINT python main.py
