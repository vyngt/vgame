# python manage.py shell < scripts/pre_check.py
# python manage.py migrate
# python manage.py collectstatic  --noinput
gunicorn --bind :80 vgame.wsgi:application
exec "$@"