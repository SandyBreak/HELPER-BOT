# -*- coding: UTF-8 -*-
    
FROM python:3.10.12-alpine

WORKDIR /bot/

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

RUN mkdir /bot/downloads

COPY . .

CMD ["python", "/bot/main.py"]
