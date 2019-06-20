FROM 3.7.3-stretch AS Build
LABEL python_version=python3.7

RUN virtualenv --no-download /env -p python3.6

ARG PORT=8080

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

RUN mkdir challenge 
WORKDIR /challenge

apt-get install odbc-postgresql

ADD . .
RUN pip install -r requirements.txt

FROM Build as default
