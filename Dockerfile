FROM python:3.9

RUN addgroup --system elyas && adduser --system --group elyas

USER elyas

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 8024
