import datetime
import logging
import logging.config
import os

import yaml


def setup_logging(config_path="logging_config.yaml", default_level=logging.info, log_output_path="logs/"):
    """Handles additional logging setup, such as appending the current date to
    the log file name for each handler. Dynamic file names are unsupported from
    from within the config yaml file.
    """
    if os.path.exists(config_path):
        with open("logging_config.yaml", "rt") as f:
            config = yaml.safe_load(f.read())

            for i in config["handlers"]:
                handler = config["handlers"][i]
                if "filename" in handler:
                    log_filename = handler["filename"]
                    base, extension = os.path.splitext(log_filename)
                    today = datetime.datetime.today()
                    log_filename = f"{log_output_path}{today.strftime('%Y_%m_%d')}_{base}{extension}"
                    print(log_filename)
                    handler["filename"] = log_filename

        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)



if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("hello")
    logger.error("cool")
    logger.critical("world")
