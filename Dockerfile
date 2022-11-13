FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update && apt install golang -y \
    && wget https://github.com/FiloSottile/mkcert/archive/v1.0.0.tar.gz \
    && tar -xvf v1.0.0.tar.gz \
    && cd mkcert-1.0.0 \
    && make \
    && cd bin \
    && cp mkcert /usr/bin/ \
    && mkcert -install 


COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

RUN cd /app/source \
    && mkcert localhost myapp.dev localhost 127.0.0.1 ::1

COPY entrypoint.sh /app/ntrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["bash", "/app/entrypoint.sh"]


CMD ["python", "/app/source/manage.py", "runserver_plus", "--cert-file", "localhost+4.pem", "--key-file", "localhost+4-key.pem", "8000"]
