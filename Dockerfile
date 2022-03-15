FROM python:3.9

# Flip to 'production' for AWS deployments
ENV ENVIRONMENT=local 

ENV DJANGO_SETTINGS_MODULE=django_globus_app.settings.base
ENV PYTHONBUFFERED=1

RUN mkdir /srv/logs

RUN apt-get update \
    && pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && chmod +x /entrypoint.sh

COPY . /backend
WORKDIR /backend

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]