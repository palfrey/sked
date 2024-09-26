FROM python:3.12

# So dbshell works
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /work
COPY . /work
RUN GOOGLE_OAUTH2_KEY=key GOOGLE_OAUTH2_SECRET=secret python manage.py collectstatic
ENV OAUTHLIB_RELAX_TOKEN_SCOPE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD bash -c "python manage.py migrate && python manage.py createcachetable && python manage.py runserver 0.0.0.0:8000"
