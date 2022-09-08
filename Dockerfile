FROM ubuntu

ENV CONF ./config_sample.toml
COPY ./config_sample.toml .

COPY ./dist/object_storage-1.0-py3-none-any.whl .
RUN apt-get update && \
    apt-get install -y python3 python3-pip
RUN python3 -m pip install wheel

RUN python3 -m pip install ./object_storage-1.0-py3-none-any.whl

ENTRYPOINT object_storage_api $CONF