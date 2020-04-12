from services.javlibrary import service as javlibrary_service
from config import base
import logging
from services.rarbg import service as rarbg_service
from random import randint


def do_asia():
    logging.basicConfig(filename='log.log',level=logging.DEBUG, format='%(levelname)s:%(asctime)s %(message)s')

    page = 7

    while page <= base.SCRAWLER_MAX_PAGE:
        requested_url = base.SCRAWLER_URL_ASIA + base.SCRAWLER_URI_ASIA % page

        javlibrary_service.do_original_source_scrawler_with_selenium(requested_url)

        page = page + 1


def do_euro():
    logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(levelname)s:%(asctime)s %(message)s')

    page = 1

    while page <= base.SCRAWLER_MAX_PAGE:
        requested_url = base.SCRAWLER_URL_EURO + base.SCRAWLER_URI_EURO % page

        rarbg_service.do_original_source_scrawler(requested_url)

        page = page + 1


def main():
    n = randint(base.IS_ASIA, base.IS_EURO)
    n = 1
    func = base.MAP_FUNC[n]

    eval(func)()


if __name__ == '__main__':
    main()
