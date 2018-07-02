FROM python:3.6-slim

WORKDIR /apigateway
ADD . /apigateway
RUN pip install -r requirements.txt
EXPOSE 80
ENV NAME apigateway
CMD ["python3","apigateway.py"]