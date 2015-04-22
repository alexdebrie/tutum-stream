FROM gliderlabs/alpine:3.1

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && rm -rf /var/cache/apk/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["/usr/bin/python", "client.py"]
