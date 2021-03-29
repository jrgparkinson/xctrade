release: python manage.py makemigrations && python manage.py migrate && python manage.py populate
web: gunicorn xctrade.wsgi
