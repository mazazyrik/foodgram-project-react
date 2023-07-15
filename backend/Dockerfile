FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram_backend/. .

RUN python3 -m pip install --upgrade pip --no-cache-dir

RUN pip3 install -r requirements.txt

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind 0:8000"]