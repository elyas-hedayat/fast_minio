FROM python:3.10


RUN adduser  myuser
USER myuser


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./app /code/app

EXPOSE 8024