#!/bin/sh
NAME="Unicooo"                                  # Name of the application
DJANGODIR=/srv/unicooo/www/unicooo             # Django project directory
GUNICORNDIR=/srv/unicooo/www             # Django project directory
SOCKFILE=/srv/unicooo/www/run/gunicorn.sock  # we will communicte using this unix socket
USER=root                                        # the user to run as
GROUP=root                                     # the group to run as
WORKER_CLASS=gevent
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=unicooo.settings.production             # which settings file should Django use
DJANGO_WSGI_MODULE=unicooo.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`, Let's rock!"

# Activate the virtual environment
cd $GUNICORNDIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
# exec gunicorn ${DJANGO_WSGI_MODULE}:application \
exec /usr/local/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --worker-class $WORKER_CLASS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-

# I'm sunkist
