
FROM python:3.6-stretch

WORKDIR /reroute

RUN pip3 install Flask \
  requests 

COPY . /reroute

EXPOSE 5000

CMD ["python3", "main.py"]