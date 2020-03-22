import logging
import os


dir = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(
    filename="%s/log.txt" % (dir),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)
logger = logging.getLogger()
