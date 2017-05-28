#!/usr/bin/env python

import logging
import signal
from time import sleep, time

import soco

logger = logging.getLogger(__name__)

class GracefulInterruptHandler(object):
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False
        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)
        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True


with GracefulInterruptHandler(sig=signal.SIGTERM) as h:
    while not h.interrupted:
        start_time = time()
        for speaker in soco.discover():
            try:
                if speaker.volume > 10:
                    logger.info("Speaker '{}' volume={} reducing...".format(speaker.player_name, speaker.volume))
                    speaker.volume -= 1
                else:
                    logger.info("Speaker '{}' volume={} maintaining...".format(speaker.player_name, speaker.volume))
            except Exception as e:
                logger.exception("Exception setting volume for speaker {}.".format(speaker.player_name))
        time_diff = time() - start_time
        sleep(max(10 - time_diff, 0))
