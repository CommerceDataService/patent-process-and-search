FROM python:2.7
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -U -r requirements.txt --src /usr/local/src
ADD . /code/
RUN mkdir /data
ADD ./data /data/
