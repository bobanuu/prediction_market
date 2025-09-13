#!/bin/bash

echo "Starting Django deployment..."

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@test.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin user already exists')"

echo "Creating sample data..."
python manage.py shell -c "exec(open('create_sample_data.py').read())"

echo "Starting Gunicorn server..."
gunicorn prediction_marketplace.wsgi:application --bind 0.0.0.0:$PORT