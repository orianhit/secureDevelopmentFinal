FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
 && apt-get install -y uwsgi uwsgi-plugin-python3 python3-virtualenv python3-dev

WORKDIR /app/source

COPY requirements.txt /app/requirements.txt
COPY requirements.prod.txt /app/requirements.prod.txt

RUN pip3 install -r /app/requirements.txt \
 && pip3 install -r /app/requirements.prod.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app

RUN adduser --disabled-password --no-create-home django \
 && chown -R django /app \
 && mkdir -p /home/django \
 && chown -R django /home/django

USER django

ENTRYPOINT ["bash", "/app/entrypoint.sh"]

CMD ["python", "/app/source/manage.py", "runserver", "0.0.0.0:8000"]
