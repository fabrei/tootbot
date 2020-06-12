FROM python:3.6.10-alpine

ARG username
ARG instance
ARG source

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY tootbot.py .
COPY cron/tootbot.cron /etc/crontabs/root

RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt && \
    sed -i "s/<username>/${username}/g" /etc/crontabs/root && \
    sed -i "s/<instance>/${instance}/g" /etc/crontabs/root && \
    sed -i "s/<source>/${source}/g" /etc/crontabs/root

CMD ["crond", "-f", "-d", "6"]
