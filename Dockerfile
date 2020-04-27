
FROM python:3.6-stretch

WORKDIR /reroute

RUN pip3 install Flask \
  FLASK_TABLE \
  requests \
  python-dateutil \
  pytz

COPY . /reroute

EXPOSE 5000

CMD ["python3", "main.py"]