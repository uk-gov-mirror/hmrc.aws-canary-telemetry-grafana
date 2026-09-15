ARG DOCKER_REPO
ARG PYTHON_VERSION

FROM ${DOCKER_REPO}/python:${PYTHON_VERSION}-slim-bookworm
ARG REQUIREMENTS_FILE
ARG PIP_INDEX_URL

WORKDIR /data

COPY ${REQUIREMENTS_FILE} /data/requirements.txt

RUN cp /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list.d/debian.sources.bak && \
    sed --in-place 's|http://|https://|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get -y upgrade && apt-get install -y zip && \
    pip install --requirement /data/requirements.txt --index-url $PIP_INDEX_URL
