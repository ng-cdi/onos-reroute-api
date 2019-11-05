
FROM python:3.6-stretch

WORKDIR /reroute

RUN pip3 install Flask \
  requests \
  gunicorn

COPY . /reroute

RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]