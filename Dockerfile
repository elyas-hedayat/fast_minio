FROM python:3.10

RUN adduser  myuser
USER myuser

WORKDIR /code

COPY ./requirements.txt /code/.

RUN  pip install --upgrade pip & pip install -r requirements.txt

COPY . /code/

EXPOSE 8024

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8024"]