import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopping_cart.settings')

app = Celery('shopping_cart')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire-carts-every-5-minutes': {
        'task': 'cart.tasks.expire_old_carts',
        'schedule': crontab(minute='*/1'),
    },
}