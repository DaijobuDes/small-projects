# Project licensed under GNU GPL v3.0
# Repository at https://github.com/DaijobuDes/small-projects
# Created by Kate Aubrey Cellan/Maine Ichinose (DaijobuDes)
#
# What's this all about?
#
# This script scrapes the posts of CIT - University's Facebook Page
# and all posts' text will be relayed to discord by using discord's webhook functionality.
# The script fetches data for every 5 minutes, unless an exception might occur, time will increase 
# by one minute with a maximum time of 10 minutes.
#
# Why did I create this?
#
# The reason why I created this is because I want to ease the access of 
# reading posts through discord instead of going to facebook's site, in which I do not
# like anymore due to the new UI that they implmented some months ago. Really, I miss the 
# old facebook's look.
#

import requests
from discord import Webhook, RequestsWebhookAdapter
from facebook_scraper import get_posts
from time import sleep
# For logging
from copy import copy
from logging import Formatter
import logging

# Log coloring start
MAPPING = {
    'DEBUG'     : 36,  # Cyan
    'INFO'      : 37,  # White
    'WARNING'   : 33,  # Yellow
    'ERROR'     : 31,  # Red
    'CRITICAL'  : 41   # White on red bg
}
PREFIX = '\u001b['
SUFFIX = '\u001b[0m'


class ColoredFormatter(Formatter):
    def __init__(self, pattern):
        Formatter.__init__(self, pattern)

    def format(self, record):
        colored_record = copy(record)
        levelname = colored_record.levelname
        seq = MAPPING.get(levelname, 37)  # Default white
        colored_levelname = ('{0}{1}m{2}{3}') \
            .format(PREFIX, seq, levelname, SUFFIX)
        colored_record.levelname = colored_levelname
        return Formatter.format(self, colored_record)

# Console logging
log = logging.getLogger('main')
fmt = "[%(asctime)s][%(name)s][%(levelname)s] = %(message)s (%(filename)s:%(lineno)d)"
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
cf = ColoredFormatter(fmt)
ch.setFormatter(cf)
log.addHandler(ch)

# Set log level
log.setLevel(logging.DEBUG)
# End of console logging

# No webhook exception, custom exception
class NoWebhookException(Exception):

    def __init__(self, messasge):
        self.message = messasge

# Global variables
g_URL = '' # Variable used to compare
g_Retries = 300


# Discord channel webhook URL
# Format is "https://discord.com/api/webhooks/<channel_id>/<webhook_token>/<endpoint>"
WEBHOOK_URL = None
# Read more here: https://discord.com/developers/docs/resources/webhook

def sendWebhook(g_URL: str, g_Retries: int):
    # Enclose in try-except 
    try:
        while True:
            if WEBHOOK_URL is None or WEBHOOK_URL == "":
                raise NoWebhookException("WEBHOOK_URL is empty")
            log.debug('Fetching recent posts.')
            for post in enumerate(get_posts('CITUniversity', pages=1)):
                if post[0] % 2 == 1:
                    if g_URL != post[1]['post_url']:
                        wb = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter())
                        wb.send(f"{post[1]['text'][:500]}...\n\nPost Link: {post[1]['post_url']}")
                        log.debug('Webhook sent.')
                        g_URL = post[1]['post_url']
                        log.debug('g_URL refreshed.')
                        log.debug("Setting g_Retries to 5 minutes.")
                        g_Retries = 300
            log.debug('Sleeping for 300 seconds.')
            sleep(300)

    # If ever the user presses CTRL + C to stop the operation
    except KeyboardInterrupt:
        log.exception("Interrupted by user.")
    # Custom exception, if no webhook URL was supplied.
    except NoWebhookException:
        log.exception("No WEBHOOK_URL was supplied.")
    # If anything happens, print out what was the reason.
    except Exception as e:
        log.exception(f"Something went wrong. Script terminated. Reason {e}.")
        log.debug(f"Retrying for {g_Retries} second(s)...")
        sleep(g_Retries)
        log.debug("Adding another minute in g_Retries...")
        g_Retries += 60
        if g_Retries >= 600:
            g_Retries = 600
        sendWebhook(g_URL, g_Retries)

if __name__ == '__main__':
    # Main variables
    g_URL = '' # Variable used to compare
    g_Retries = 300
    log.debug(f"Executing function (void) sendWebhook() with arguments g_URL={g_URL}, g_Retries={g_Retries}")
    sendWebhook(g_URL, g_Retries)
