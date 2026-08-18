#!/usr/bin/env bash

set -e

PROJECT_GIT_URL='https://github.com/Manou3737/profiles-rest-api.git'

PROJECT_BASE_PATH='/usr/local/apps'
VIRTUALENV_BASE_PATH='/usr/local/virtualenvs'

PROJECT_PATH="$PROJECT_BASE_PATH/profiles-rest-api"
VENV_PATH="$VIRTUALENV_BASE_PATH/profiles_api"
DJANGO_PATH="$PROJECT_PATH/src/profiles_project"

echo "Installing dependencies..."

apt-get update
apt-get install -y \
    locales \
    python3-dev \
    python3-venv \
    sqlite3 \
    python3-pip \
    supervisor \
    nginx \
    git

echo "Configuring locale..."

locale-gen en_GB.UTF-8

echo "Preparing application directory..."

mkdir -p "$PROJECT_BASE_PATH"

if [ ! -d "$PROJECT_PATH/.git" ]; then
    git clone --branch modernize-python314 "$PROJECT_GIT_URL" "$PROJECT_PATH"
fi

echo "Preparing virtual environment..."

mkdir -p "$VIRTUALENV_BASE_PATH"

if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

echo "Installing Python dependencies..."

"$VENV_PATH/bin/pip" install -r "$PROJECT_PATH/requirements.txt"

echo "Running Django checks..."

cd "$DJANGO_PATH"

"$VENV_PATH/bin/python" manage.py check

echo "Running migrations..."

"$VENV_PATH/bin/python" manage.py migrate

echo "Collecting static files..."

"$VENV_PATH/bin/python" manage.py collectstatic --noinput

echo "Configuring Supervisor..."

SUPERVISOR_CONF="/etc/supervisor/conf.d/profiles_api.conf"

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "Supervisor configuration already exists; preserving server environment variables."
else
    cp "$PROJECT_PATH/deploy/supervisor_profiles_api.conf" "$SUPERVISOR_CONF"
fi

supervisorctl reread
supervisorctl update
supervisorctl restart profiles_api

echo "Configuring Nginx..."

cp "$PROJECT_PATH/deploy/nginx_profiles_api.conf" \
   /etc/nginx/sites-available/profiles_api.conf

rm -f /etc/nginx/sites-enabled/default

ln -sf \
   /etc/nginx/sites-available/profiles_api.conf \
   /etc/nginx/sites-enabled/profiles_api.conf

nginx -t
systemctl restart nginx

echo "Deployment completed successfully!"
