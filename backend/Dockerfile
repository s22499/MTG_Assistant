FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 4000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "4000"]