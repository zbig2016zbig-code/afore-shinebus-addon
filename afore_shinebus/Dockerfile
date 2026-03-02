FROM python:3.11-slim

WORKDIR /app

COPY shinebus.py .
COPY config.yaml .

RUN pip install paho-mqtt

CMD ["python3", "shinebus.py"]

