FROM python:3.7.3-stretch AS Build

RUN mkdir challenge 
WORKDIR /challenge


RUN apt-get update && \
	apt-get install -y unixodbc-dev g++ odbc-postgresql

ADD . .
RUN pip install -r requirements.txt

FROM Build as default
