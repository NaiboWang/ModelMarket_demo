import time
from app_test import app

@app.task
def add(x, y):
    time.sleep(1)
    return x + y