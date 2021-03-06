FROM python:3.6.1-alpine

RUN apk update \
  && apk add \
    build-base \
    libpq \
        # Pillow dependencies
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    ttf-freefont

RUN apk add --update tzdata
ENV TZ=America/LosAngeles

RUN mkdir /usr/src/app
RUN mkdir /ssl

WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir static
ENV PYTHONUNBUFFERED 1
ENV LIBRARY_PATH=/lib:/usr/lib

COPY . .

ENTRYPOINT python main.py
