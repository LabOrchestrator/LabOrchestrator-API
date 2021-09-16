FROM python:3.8
LABEL maintainer="Marco Schlicht <git@privacymail.dev>"

ENV PYTHONUNBUFFERED=1
ENV LOCALDEVMODE=False

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# required for postgres
RUN apt-get install libpq-dev -y

# install requirements
RUN mkdir -p /opt/app/
WORKDIR /opt/app/
COPY requirements.txt /opt/app/
RUN pip install -r requirements.txt

# copy application with right permissions
COPY . /opt/app/
RUN mkdir -p /opt/app/static
RUN chown -R www-data:www-data /opt/app

EXPOSE 5000

CMD ["/opt/app/docker-entrypoint.sh"]
