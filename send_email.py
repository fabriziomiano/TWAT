import os 
import logging
import logging.handlers
from classes.EDM import EDM
from classes.BufferingSMTPHandler import BufferingSMTPHandler
from settings.config import MAILHOST, FROM, TO, SUBJECT, RANGE_ACCEPTED
from settings.constants import PROJECT_HOME
from utils.webpage_tools import bad_page_contents
from utils.misc import get_logger


DB_PATH = os.path.join(PROJECT_HOME,'archive_db.json')
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]

edm = EDM(DB_PATH, TEMPLATE_FIELDS)

header_fields = ('branch', 'project', 'platform')
contents = bad_page_contents(edm, header_fields)

# Send the email
email_logger = get_logger(__name__)
email_logger.setLevel(logging.INFO)
SUBJECT = "EDM monitoring: daily news"
email_news = BufferingSMTPHandler(MAILHOST, FROM, TO, SUBJECT, 100)
email_news.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
email_news.setFormatter(formatter)
email_logger.addHandler(email_news)

if len(contents) != 0:
    email_logger.info("Good morning!")
    email_logger.info("Sorry to give you bad news: there are items in the bad list.")
    email_logger.info("\n")
    email_logger.info("Please check the website")
    email_logger.info("https://test-atrvshft.web.cern.ch/test-atrvshft/TriggerEDMSizeMonitoring/webpage/")
else:
    email_logger.info("Good morning!")
    email_logger.info("Good news: there are no items in the bad list :)")
    email_logger.info("\n")
    email_logger.info("Have a lovely day")
    email_logger.info("\n")
    email_logger.info("P.S.: You can still check the website")
    email_logger.info("https://test-atrvshft.web.cern.ch/test-atrvshft/TriggerEDMSizeMonitoring/webpage/")
