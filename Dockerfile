############################################################
# Dockerfile to build Flask App
# Based on
############################################################

# Set the base image
FROM debian:stretch-slim

# File Author / Maintainer
MAINTAINER Carlos Tighe

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    python3 \
    python3-dev\
    python3-pip \
    vim \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*

# Copy over and install the requirements
COPY ./app/requirements.txt /var/www/vowr-container-apache/app/requirements.txt
RUN python3 -m pip install -r /var/www/vowr-container-apache/app/requirements.txt

# Copy over the apache configuration file and enable the site
COPY ./apache/vowr-container-apache.conf /etc/apache2/sites-available/vowr-container-apache.conf
RUN a2ensite vowr-container-apache
RUN a2enmod headers

# Copy over the wsgi file
COPY ./vowr-container-apache.wsgi /var/www/vowr-container-apache/vowr-container-apache.wsgi

COPY ./run.py /var/www/vowr-container-apache/run.py
COPY ./app /var/www/vowr-container-apache/app/

RUN a2dissite 000-default.conf
RUN a2ensite vowr-container-apache.conf

EXPOSE 80

WORKDIR /var/www/vowr-container-apache

# CMD ["/bin/bash"]
CMD  /usr/sbin/apache2ctl -D FOREGROUND
# The commands below get apache running but there are issues accessing it online
# The port is only available if you go to another port first
# ENTRYPOINT ["/sbin/init"]
# CMD ["/usr/sbin/apache2ctl"]
