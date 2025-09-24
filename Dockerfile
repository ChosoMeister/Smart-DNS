FROM alpine:edge
LABEL maintainer="Mustafa Tayefi <ChosoMeister@gmail.com>"

RUN apk add --no-cache py3-pip nginx nginx-mod-stream --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/
RUN sh -c 'mkdir -p /run/openrc/ && mkdir -p /run/nginx'
RUN pip3 install --no-cache-dir --break-system-packages dnslib


COPY nginx.conf /etc/nginx/nginx.conf
COPY dns.py /opt/dns.py
COPY domains /opt/domains
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
