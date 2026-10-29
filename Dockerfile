
FROM python:3.12-slim

WORKDIR /app

COPY monitor.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "monitor.py"]
