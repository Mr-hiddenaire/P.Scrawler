from pyquery import PyQuery
from config import base
from services.cloudflare import service as cloudflare_service
from models import db
from models import contents_model
from services.searcher import torrent_searcher
from utils.selenium.chrome import browser
import time


def parse_columns(origin_html_list):
    doc = PyQuery(origin_html_list)

    htmls_list = doc('.video').items()

    for list_html in htmls_list:
        column_result_list = parse_column_list(list_html)

        origin_html_detail = cloudflare_service.get_data(column_result_list['detail_url'])

        column_result_detail = parse_column_detail(origin_html_detail)

        column_result_list['tags'] = column_result_detail['tags']

        torrent_url = torrent_searcher.find_torrent(column_result_list['unique_id'])

        column_result_list['torrent_url'] = torrent_url

        save_data(column_result_list)


def save_data(data):
    db_session = db.init()

    row = db_session.query(contents_model.Contents).filter(contents_model.Contents.unique_id == data['unique_id']).first()

    if row is None:
        if data['torrent_url'] is not None:
            new_contents = contents_model.Contents(
                name=data['name'],
                unique_id=data['unique_id'],
                tags=data['tags'],
                type=1,
                thumb_url=data['image_url'],
                torrent_url=data['torrent_url'],
            )

            db_session.add(new_contents)
            db_session.commit()


def parse_column_list(html):
    doc = PyQuery(html)

    unique_id = doc('.id').text()

    name = doc('.title').text()

    image_url = 'https://' + doc('img').attr('src').replace('//', '')

    detail_url = base.SCRAWLER_URL_ASIA + doc('a').attr('href').replace('./', '')

    result = {
        'unique_id': unique_id,
        'name': name,
        'image_url': image_url,
        'detail_url': detail_url,
    }

    return result


def parse_column_detail(origin_html_detail):
    result = parse_tags(origin_html_detail)

    return result


def parse_tags(origin_html_detail):
    tags = []

    doc = PyQuery(origin_html_detail)

    htmls_detail = doc('.genre').items()

    for html_detail in htmls_detail:
        doc_tag = PyQuery(html_detail)

        tag = doc_tag('a').text()

        tags.append(tag)

    result = {
        'tags': ','.join(tags)
    }

    return result


def do_original_source_scrawler(url):
    original_html = cloudflare_service.get_data(url)

    parse_columns(original_html)


def do_original_source_scrawler_with_selenium(url):
    """ driver initialization """
    driver = browser.get_driver()

    driver.get(url)

    """ sleep 6 sec to wait cf protection """
    time.sleep(6)

    htmls = driver.page_source

    driver.close()

    parse_columns_with_selenium(htmls)


def parse_columns_with_selenium(origin_html_list):
    db_session = db.init()

    doc = PyQuery(origin_html_list)

    htmls_list = doc('.video').items()

    for list_html in htmls_list:
        column_result_list = parse_column_list(list_html)

        row = db_session.query(contents_model.Contents).filter(contents_model.Contents.unique_id == column_result_list['unique_id']).first()

        if row is not None:
            continue

        """ driver initialization """
        driver = browser.get_driver()

        driver.get(column_result_list['detail_url'])

        """ sleep 6 sec to wait cf protection """
        time.sleep(6)

        detail_html = driver.page_source
        driver.close()

        column_result_detail = parse_column_detail(detail_html)

        column_result_list['tags'] = column_result_detail['tags']

        torrent_path = torrent_searcher.find_torrent(column_result_list['unique_id'])

        column_result_list['torrent_url'] = torrent_path

        save_data(column_result_list)
