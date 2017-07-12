#!/bin/sh
apt-get -y update
apt-get -y install docker-compose
docker-compose build
docker-compose up

