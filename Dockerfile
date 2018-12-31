# Pull from Alpine image
FROM alpine

# Set metadata for image
LABEL maintainer "Jacob House <me@jwfh.ca>"
LABEL description "VOWR Music Librarian with Nginx/uWSGI/Flask on Alpine Linux"

# Ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# Copy python requirements file
COPY app/requirements.txt /tmp/requirements.txt

# Install 
RUN apk add --no-cache \
    curl \
    pkgconfig \
    openssl-dev \
    libffi-dev \
    musl-dev \
    make \
    gcc \
    python3 \
    python3-dev \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    python3 -m pip install --upgrade pip setuptools && \
    python3 -m pip install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# Make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# Copy the Nginx global conf
COPY nginx/nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY nginx/vowr-container-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Copy application files 
COPY ./app /app
WORKDIR /

CMD ["/usr/bin/supervisord"]
