FROM python:3

# So dbshell works
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /work
COPY . /work
CMD bash -c "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"