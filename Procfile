release: python manage.py migrate && python manage.py createcachetable
web: gunicorn sked.wsgi --log-file -