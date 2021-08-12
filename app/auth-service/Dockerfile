FROM python:3.7-slim

EXPOSE 8080

RUN mkdir /app
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app

CMD ["python", "/app/app.py"]
