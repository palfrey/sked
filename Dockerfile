FROM python:3

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /work
COPY . /work
CMD bash -c "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"