FROM python:3.13-slim-bookworm
LABEL org.opencontainers.image.source="https://github.com/notaussie/bustinel"
LABEL org.opencontainers.image.title="Bustinel"
LABEL org.opencontainers.image.description="Bustinel is a Python application that generates trip records for GTFS-RT feeds."
LABEL org.opencontainers.image.licenses="AGPL-3.0-only"
LABEL org.opencontainers.image.authors="NotAussie <notaussie@duck.com>"
LABEL org.opencontainers.image.vendor="NotAussie"

WORKDIR /app

COPY ./src /app
COPY ./requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]