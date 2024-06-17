from price_updater import main as price_updater
from appstore import main as appstore

from loggingInit import initLogger

import logging

logger = logging.getLogger(__name__)


def main():
    initLogger()

    price_updater()
    appstore()


if __name__ == "__main__":
    main()
