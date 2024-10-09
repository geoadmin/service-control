import os

import yaml

from .settings_base import *  # pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = False


# Read configuration from file
def get_logging_config() -> dict[str, object]:
    '''Read logging configuration
    Read and parse the yaml logging configuration file passed in the environment variable
    LOGGING_CFG and return it as dictionary
    Note: LOGGING_CFG is relative to the root of the repo
    '''
    log_config_file = env('LOGGING_CFG', default='app/config/logging-cfg-local.yml')
    if log_config_file.lower() in ['none', '0', '', 'false', 'no']:
        return {}
    log_config = {}
    with open(BASE_DIR / log_config_file, 'rt', encoding="utf-8") as fd:
        log_config = yaml.safe_load(os.path.expandvars(fd.read()))
    return log_config
