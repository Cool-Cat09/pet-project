import logging

def logger(level: int = logging.INFO):
    """get configurated logger
    
    return: logger: type - python-logger
    """

    
    log = logging.getLogger(__name__)
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='[%(asctime)s.%(msecs)03d %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s]'
    )
    return log