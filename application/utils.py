import logging


def get_logger(name=__file__, level=logging.INFO):
    """ Returns a logger object """

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s %(process)d [%(levelname)s] %(message)s")
    console.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(console)
    return logger
