FROM python:3.6-slim

RUN mkdir /shopservice
WORKDIR /shopservice
ADD . /shopservice
RUN pip install -r requirements.txt
EXPOSE 80
ENV NAME shopservice
CMD ["python3","shopservice.py"]