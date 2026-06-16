FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=120 --retries=3 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
