import datetime
import logging
import os
import sys
import traceback


def log(message, exception, level=logging.DEBUG):
    if exception is not None:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)[-1]
        filename = os.path.split(tb.filename)[1]
        msg = (str(exception) + ' - ' + message) if message is not None else str(exception)
        logging.log(level, msg, extra={'lineno2': str(tb.lineno), 'filename2': filename})
    else:
        if message is not None:
            logging.log(level, message, extra={'lineno2': '', 'filename2': ''})


class Log:

    @staticmethod
    def init(app_folder):

        if not os.path.exists(os.path.join(app_folder, 'logs')):
            os.makedirs(os.path.join(app_folder, 'logs'))

        # todo: dev utility - change filename to full date
        # log_filename = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S.log")
        log_filename = datetime.datetime.now().strftime("%Y-%m-%d.log")

        logging.basicConfig(filename=os.path.join(app_folder, 'logs', log_filename),
                            filemode='a',
                            # format='%(asctime)s,%(msecs)d p%(process)s %(name)s %(levelname)s %(message)s',
                            format='[%(asctime)s] %(levelname)s {%(filename2)s:%(lineno2)s} - %(message)s',
                            # datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    @staticmethod
    def info(message=None, exception=None):
        log(message, exception, logging.INFO)

    @staticmethod
    def debug(message=None, exception=None):
        log(message, exception, logging.DEBUG)

    @staticmethod
    def error(message=None, exception=None):
        log(message, exception, logging.ERROR)

