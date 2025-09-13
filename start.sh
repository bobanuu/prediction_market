#!/bin/bash
# Startup script for Railway deployment

echo "Starting Django application..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Create sample data
echo "Creating sample data..."
python manage.py shell -c "
try:
    exec(open('create_sample_data.py').read())
    print('Sample data created successfully')
except Exception as e:
    print(f'Error creating sample data: {e}')
"

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn prediction_marketplace.wsgi:application --bind 0.0.0.0:$PORT
