# docker/pig/Dockerfile

FROM openjdk:8-jdk-slim

ENV PIG_VERSION=0.17.0
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$PIG_HOME/bin

RUN apt-get update && \
    apt-get install -y wget tar python3 python3-pip && \
    wget https://downloads.apache.org/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz && \
    tar -xvzf pig-${PIG_VERSION}.tar.gz -C /opt && \
    mv /opt/pig-${PIG_VERSION} $PIG_HOME && \
    rm pig-${PIG_VERSION}.tar.gz

WORKDIR /pig
