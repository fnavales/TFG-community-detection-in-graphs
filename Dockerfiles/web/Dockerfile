FROM python:3

RUN mkdir /code
WORKDIR /code
ADD . /code/

RUN apt-get -y update && apt-get -y install build-essential libxml2-dev zlib1g-dev python-dev pkg-config libffi-dev libcairo-dev
RUN python3 -m pip install -r requirements.txt


