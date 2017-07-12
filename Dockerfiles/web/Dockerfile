FROM python:3

RUN mkdir /code
WORKDIR /code
ADD . /code/

RUN apt-get -y update && apt-get install -y libigraph0-dev
RUN python3 -m pip install -r requirements.txt


