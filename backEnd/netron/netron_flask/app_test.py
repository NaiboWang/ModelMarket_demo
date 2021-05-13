from celery import Celery

app = Celery('proj', include=['tasks'])
app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()