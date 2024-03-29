FROM python:3.8

# So dbshell works
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /work
COPY . /work
ENV OAUTHLIB_RELAX_TOKEN_SCOPE=1
CMD /work/wait-for-it.sh postgres:5432 --timeout=0 --strict -- bash -c "python3 manage.py migrate && python3 manage.py createcachetable && python3 manage.py runserver 0.0.0.0:8000"