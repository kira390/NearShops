FROM python:3.6-slim

COPY . /authentication_service
WORKDIR /authentication_service
RUN pip install -r requirements.txt
EXPOSE 80
ENV NAME authentication_service
CMD ["python","authservice.py"]