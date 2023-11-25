FROM python:3.9

RUN addgroup --system elyas && adduser --system --group elyas

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

WORKDIR /app

USER elyas

EXPOSE 8024
