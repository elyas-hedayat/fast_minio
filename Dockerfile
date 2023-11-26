FROM python:3.10

RUN addgroup --system elyas && adduser --system --group elyas

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

WORKDIR /app

COPY ./docker_entrypoint.sh /

EXPOSE 8023

USER elyas

ENTRYPOINT ["sh", "/docker_entrypoint.sh"]