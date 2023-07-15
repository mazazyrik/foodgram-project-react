FROM python:3.9

RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y xz-utils
RUN apt-get install -y libfontconfig1 libxrender1 libxext6
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xvJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cp wkhtmltox/bin/wkhtmlto* /usr/bin/

WORKDIR /foodgram_backend
COPY ./ ./
RUN python3 -m pip install --upgrade pip --no-cache-dir
RUN pip3 install -r requirements.txt

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind", "0:8000"]