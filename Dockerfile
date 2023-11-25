FROM python:3.10


RUN adduser  myuser
USER myuser

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --no-cache-dir --upgrade && pip install -r requirements.txt

COPY . /code

EXPOSE 8024