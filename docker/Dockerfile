FROM python:3.10

RUN addgroup --system elyas && adduser --system --group elyas

COPY ./requirments /requirments

RUN pip install --upgrade pip && pip install -r /requirments/base.txt

COPY . /app

WORKDIR /app

EXPOSE 8023

USER elyas