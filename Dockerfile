FROM python:3.10-slim

RUN apt-get update && apt-get install -y tcc gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install flask twilio

CMD ["python", "app.py"]
