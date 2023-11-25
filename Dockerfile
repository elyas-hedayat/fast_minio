FROM python:3.9

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

COPY ./docker_entrypoint.sh /

ENTRYPOINT ["sh", "/docker_entrypoint.sh"]