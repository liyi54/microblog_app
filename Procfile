web: flask db upgrade; flask translate compile; python tests.py; gunicorn microblog_app:app
worker: rq worker -u $REDIS_URL microblog-tasks