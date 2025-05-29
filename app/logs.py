import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

custom_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)
custom_handler.setFormatter(formatter)
logger.addHandler(custom_handler)
