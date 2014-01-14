#!/bin/bash
APP_COMPONENTS="$*"
APP_DIR=/opt/apps/scivm-dashboard
ADMIN_PASS=${ADMIN_PASS:-}
DEBUG=${DEBUG:-True}
CELERY_WORKERS=${CELERY_WORKERS:-4}
REDIS_HOST=${REDIS_HOST:-127.0.0.1}
REDIS_PORT=${REDIS_PORT:-6379}
DB_TYPE=${DB_TYPE:-postgresql_psycopg2}
DB_NAME=${DB_NAME:-scivmcom}
DB_USER=${DB_USER:-nobody}
DB_PASS=${DB_PASS:-scivm}
DB_HOST=${DB_HOST:-172.17.0.46}
DB_PORT=${DB_PORT:-5432}
VE_DIR=/opt/ve/scivm-dashboard
EXTRA_CMD=${EXTRA_CMD:-}
EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS:-}
CONFIG=$APP_DIR/scivm/local_settings.py
UPDATE_APP=${UPDATE_APP:-}
REVISION=${REVISION:-master}
LOG_DIR=/var/log/scivm
NGINX_RESOLVER=${NGINX_RESOLVER:-`cat /etc/resolv.conf | grep ^nameserver | head -1 | awk '{ print $2; }'`}
SUPERVISOR_CONF=/opt/supervisor.conf
NGINX_PORT=${NGINX_PORT:-443}
DJANGO_PORT=${DJANGO_PORT:-5000}

echo "App Components: ${APP_COMPONENTS}"

# check for db link
if [ ! -z "$DB_PORT_5432_TCP_ADDR" ] ; then
    DB_TYPE=postgresql_psycopg2
    DB_NAME=${DB_ENV_DB_NAME:-scivmcom}
    DB_USER=${DB_ENV_DB_USER:-nobody}
    DB_PASS=${DB_ENV_DB_PASS:-scivm}
    DB_HOST=${DB_PORT_5432_TCP_ADDR}
    DB_PORT=${DB_PORT_5432_TCP_PORT}
fi
# check for redis link
if [ ! -z "$REDIS_PORT_6379_TCP_ADDR" ] ; then
    REDIS_HOST="${REDIS_PORT_6379_TCP_ADDR:-$REDIS_HOST}"
    REDIS_PORT=${REDIS_PORT_6379_TCP_PORT:-$REDIS_PORT}
fi
mkdir -p $LOG_DIR
cd $APP_DIR
echo "REDIS_HOST=\"$REDIS_HOST\"" > $CONFIG
echo "REDIS_PORT=$REDIS_PORT" >> $CONFIG
cat << EOF >> $CONFIG
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.${DB_TYPE}',
        'NAME': '${DB_NAME}',
        'USER': '${DB_USER}',
        'PASSWORD': '${DB_PASS}',
        'HOST': '${DB_HOST}',
        'PORT': '${DB_PORT}',
    }
}
DEBUG = ${DEBUG}
EOF

# deploy
if [ ! -z "$UPDATE_APP" ] ; then
    git fetch
    git reset --hard
    git checkout --force $REVISION
    git pull --ff-only origin $REVISION
fi
# supervisor
cat << EOF > $SUPERVISOR_CONF
[supervisord]
nodaemon=false

[unix_http_server]
file=/var/run//supervisor.sock
chmod=0700

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run//supervisor.sock

EOF

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep app`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:app]
priority=10
directory=/opt/apps/scivm-dashboard
command=/usr/local/bin/uwsgi
    --http-socket 0.0.0.0:5000
    -p 4
    -b 32768
    -T
    --master
    --max-requests 5000
    -H /opt/ve/scivm-dashboard
    --static-map /static=/opt/apps/scivm-dashboard/static
    --static-map /static=/opt/ve/scivm-dashboard/lib/python2.7/site-packages/django/contrib/admin/static
    --module wsgi:application
user=root
autostart=true
autorestart=true
stopsignal=QUIT
stdout_logfile=/var/log/scivm/app.log
stderr_logfile=/var/log/scivm/app.err

EOF
fi

if [ -z "$APP_COMPONENTS" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:redis]
priority=10
directory=/var/lib/redis
command=redis-server
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/scivm-dashboard/redis.log
stderr_logfile=/var/log/scivm-dashboard/redis.err

EOF
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep master-worker`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:master-worker]
priority=99
directory=/opt/apps/scivm-dashboard
command=/opt/ve/scivm-dashboard/bin/python manage.py celery worker -B --scheduler=djcelery.schedulers.DatabaseScheduler -E -c ${CELERY_WORKERS}
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/scivm-dashboard/master-worker.log
stderr_logfile=/var/log/scivm-dashboard/master-worker.err

EOF
fi

if [ ! -z "`echo $APP_COMPONENTS | grep "^worker"`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:worker]
priority=99
directory=/opt/apps/scivm-dashboard
command=/opt/ve/scivm-dashboard/bin/python manage.py celery worker --scheduler=djcelery.schedulers.DatabaseScheduler -E -c ${CELERY_WORKERS}
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/scivm-dashboard/worker.log
stderr_logfile=/var/log/scivm-dashboard/worker.err

EOF
fi

if [ -z "$APP_COMPONENTS" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:nginx]
priority=20
directory=/etc/nginx
command=/usr/sbin/nginx
    -p /etc/nginx/ 
    -c /opt/apps/scivm-dashboard/.docker/nginx.conf
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/scivm-dashboard/nginx.log
stderr_logfile=/var/log/scivm-dashboard/nginx.err

EOF
fi

# nginx resolver
cat << EOF > $APP_DIR/.docker/nginx.conf
daemon off;
worker_processes  1;
error_log $LOG_DIR/nginx_error.log;

events {
  worker_connections 1024;
}

http {
  server {
    listen $NGINX_PORT ssl;
    access_log $LOG_DIR/nginx_access.log;
    ssl_certificate      $APP_DIR/.docker/server.crt;
    ssl_certificate_key  $APP_DIR/.docker/server.key;

    # keepalive is higher for ssl
    keepalive_timeout 70;

    location / {
      proxy_pass http://127.0.0.1:$DJANGO_PORT;
      proxy_set_header Host \$http_host;
      proxy_set_header X-Forwarded-Host \$host;
      proxy_set_header X-Real-IP \$remote_addr;
      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_set_header X-Scheme \$scheme;
      proxy_set_header X-Forwarded-Protocol \$scheme;
      proxy_connect_timeout 10;
      proxy_read_timeout 10;
    }

  }
}
EOF
if [ ! -z "$EXTRA_CMD" ]; then
    /bin/bash -c "$EXTRA_CMD"
fi
$VE_DIR/bin/pip install -r requirements.txt
if [ ! -z "$EXTRA_REQUIREMENTS" ]; then
    $VE_DIR/bin/pip install $EXTRA_REQUIREMENTS
fi
$VE_DIR/bin/python manage.py syncdb --noinput
$VE_DIR/bin/python manage.py migrate --noinput
$VE_DIR/bin/python manage.py create_api_keys
if [ ! -z "$ADMIN_PASS" ] ; then
    $VE_DIR/bin/python manage.py update_admin_user --username=admin --password=$ADMIN_PASS
fi
supervisord -c $SUPERVISOR_CONF -n
