FROM python:3.9

WORKDIR /code


RUN pip install virtualenv

RUN mkdir /code/venv

RUN python -m venv /code/venv

RUN . /code/venv/bin/activate

COPY ./requirements.txt /code/venv/
RUN pip install -r /code/venv/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8023"]