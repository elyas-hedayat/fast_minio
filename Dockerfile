#
FROM python:3.9

#
WORKDIR /code


# Install virtualenv
RUN pip install virtualenv

# Create venv directory
RUN mkdir /code/venv

# Set up virtual environment
RUN python -m venv /code/venv

# Activate venv
RUN . /code/venv/bin/activate

# Install requirements
COPY ./requirements.txt /code/venv/
RUN pip install -r /code/venv/requirements.txt

# Copy app
COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8023"]