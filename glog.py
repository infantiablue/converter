import os
from google.cloud import logging

# TODO : auto set environment variable GOOGLE_APPLICATION_CREDENTIALS for production environment
APP_PATH = os.path.dirname(os.path.realpath(__file__))
logging_client = logging.Client.from_service_account_json(
    APP_PATH + '/gcloud.json')


def write_log(logger_name, msg, level):
    """Writes log entries to the given logger."""
    # This log can be found in the Cloud Logging console under 'Custom Logs'.
    logger = logging_client.logger(logger_name)

    # Struct log. The struct can be any JSON-serializable dictionary.
    if type(msg) == dict:
        logger.log_struct(msg, severity=level)
    else:
        logger.log_text(msg, severity=level)
    # print('Wrote logs to {}.'.format(logger.name))


def list_entries(logger_name):
    """Lists the most recent entries for a given logger."""
    logger = logging_client.logger(logger_name)
    print('Listing entries for logger {}:'.format(logger.name))
    for entry in logger.list_entries():
        timestamp = entry.timestamp.isoformat()
        print('* {}: {}'.format(timestamp, entry.payload))


def delete_logger(logger_name):
    """Deletes a logger and all its entries.
    Note that a deletion can take several minutes to take effect.
    """
    logger = logging_client.logger(logger_name)
    logger.delete()
    print('Deleted all logging entries for {}'.format(logger.name))


if __name__ == '__main__':
    list_entries('download')
