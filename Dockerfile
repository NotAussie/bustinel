FROM python:3.13-slim-bookworm
LABEL org.opencontainers.image.source="https://github.com/notaussie/bustinel"

WORKDIR /app

COPY ./src /app
COPY ./requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]