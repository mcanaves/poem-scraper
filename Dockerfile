FROM python:3.8-alpine

ARG APP_ENV=production

ENV APP_ENV=$APP_ENV
ENV PYTHONPATH=/opt
ENV PYTHONUNBUFFERED=1

WORKDIR /opt

COPY ./requirements ./requirements

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev \
 && apk add --no-cache libxslt \
 && pip install --no-cache-dir --disable-pip-version-check -r ./requirements/${APP_ENV}.txt \
 && apk del .build-deps \
 && rm -rf ./requirements

COPY . /opt

ENTRYPOINT [ "python", "-m", "scraper.cli" ]
