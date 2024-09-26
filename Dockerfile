FROM python:3.12

# So dbshell works
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /work
COPY . /work
ENV OAUTHLIB_RELAX_TOKEN_SCOPE=1
CMD bash -c "python3 manage.py migrate && python3 manage.py createcachetable && python3 manage.py runserver 0.0.0.0:8000"
