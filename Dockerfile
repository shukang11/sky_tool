FROM python:3

# MAINTAINER 804506054 "804506054@qq.com"
WORKDIR /sky_tool

RUN apt-get update -y && \  
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /sky_tool/requirements.txt


RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]

CMD [ "python", "manager.py" ]