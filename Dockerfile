FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Django deployment..."\n\
echo "Running migrations..."\n\
python manage.py migrate\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "Creating superuser if needed..."\n\
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('\''admin'\'', '\''admin@test.com'\'', '\''admin123'\'') if not User.objects.filter(username='\''admin'\'').exists() else None"\n\
echo "Creating sample data..."\n\
python manage.py shell -c "exec(open('\''create_sample_data.py'\'').read())"\n\
echo "Starting Gunicorn server..."\n\
gunicorn prediction_marketplace.wsgi:application --bind 0.0.0.0:$PORT' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose port
EXPOSE $PORT

# Run startup script
CMD ["./start.sh"]
