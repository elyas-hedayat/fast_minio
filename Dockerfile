#
FROM python:3.9

#
WORKDIR ./

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./main.py /code/app
COPY ./rabbit.py /code/app
#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port=8035"]
