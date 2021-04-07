FROM --platform=linux/amd64 ubuntu:18.04 AS myubuntu
RUN mkdir /code
WORKDIR /code
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl1.0.0 \
    libasound2 \
    python3.6

RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
ADD . /code/
ENV LC_ALL=C.UTF-8 
ENV LANG=C.UTF-8
RUN pip3 install -r ./requirements.txt
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader averaged_perceptron_tagger
EXPOSE 8000

# docker build --network=host -t testinstall2 .
# docker tag testinstall2:latest testinstall:staging
