FROM ubuntu:latest
ADD . /todo
WORKDIR /todo
RUN apt-get -y update && apt-get -y install build-essential libxml2-dev python3-dev python3-pip python3
RUN python3 -m pip install --upgrade pip
RUN apt-get install -y libigraph0-dev
RUN python3 -m pip install -r requirements.txt
CMD /usr/local/bin/igraph
