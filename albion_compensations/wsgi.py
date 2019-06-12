"""
WSGI config for albion_compensations project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

from albion_compensations.publisher import Publisher

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)
logger.info("Albion webscraper is up")


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'albion_compensations.settings')

publisher = Publisher()

application = get_wsgi_application()
