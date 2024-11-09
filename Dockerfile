FROM python:3.12-slim

WORKDIR /app

COPY ./abcd_server/* .
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
