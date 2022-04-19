FROM ubuntu:20.04

WORKDIR /app
ADD . /app
RUN set -xe \
    && apt-get update \
    && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python3", "app.py" ]