import sys
import logging
 
logging.basicConfig(filename="/tmp/wsgi.log",level=logging.DEBUG)
sys.path.insert(0,"/var/www/flask_login")
 
from src.app import app as application 
# application.secret_key = ''
