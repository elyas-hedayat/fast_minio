FROM minio/minio

# Install Python and Pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy and install requirements
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

# Copy FastAPI app
COPY ./main.py /opt/app
COPY ./rabbit.py /opt/app
WORKDIR /opt/app

# Configure MinIO

ENV MINIO_ROOT_USER=user
ENV MINIO_ROOT_PASSWORD=password
ENV MINIO_ACCESS_KEY=minio
ENV MINIO_SECRET_KEY=minio123
VOLUME /data

# Expose ports
EXPOSE 8035 9010

# Start services
CMD ["bash", "-c", "minio server /data --address :9010 & uvicorn main:app --host 0.0.0.0 --port 8035"]