FROM ubuntu:bionic

# install tzdata and qbzr
RUN apt-get update && apt-get install -y tzdata qbzr \
    && rm -rf /var/lib/apt/lists/*

# set local timezone
ENV TZ=US/Eastern
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# working directory
WORKDIR /workdir