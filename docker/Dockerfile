FROM python:3.10

RUN addgroup --system elyas && adduser --system --group elyas

COPY ../requirments/base.txt .

RUN pip install --upgrade pip && pip install -r base.txt

COPY .. /app

WORKDIR /app

EXPOSE 8023

USER elyas

ENTRYPOINT ["sh", "/docker_entrypoint.sh"]