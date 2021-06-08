web: gunicorn app:app
worker: celery -A app.celery worker -l INFO --concurrency 2 --without-gossip --without-mingle --without-heartbeat