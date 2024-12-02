from authentication import settings

port = int(settings.APPLICATION_PORT)
bind = f"0.0.0.0:{port}"
workers = int(settings.GUNICORN_WORKERS)
worker_class = "authentication.workers.UvicornWorker"
accesslog = "-"
