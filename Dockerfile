FROM python:3.10.7

COPY . /code

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system
RUN pip install gunicorn


RUN chmod +x scripts/entrypoint.sh

EXPOSE 80/tcp

ENTRYPOINT ["sh", "scripts/entrypoint.sh"]