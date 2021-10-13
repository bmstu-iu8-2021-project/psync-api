FROM python:3.6

RUN mkdir -p /usr/scr/app/
WORKDIR /usr/scr/app/

COPY . /usr/scr/app/

#RUN apt-get update
#RUN apt-get -y install postgresql-client

#RUN chmod +x wait-for-postgres.sh

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
