FROM python:3.10


RUN adduser -D myuser
USER myuser

WORKDIR /code


COPY ./requirements.txt .

RUN  pip install --upgrade pip & pip install -r requirements.txt

COPY ./ .

EXPOSE 8024