from config import base
from config import coordinate
import re
import time
from PIL import Image
import pytesseract
from utils.selenium.chrome import browser
from selenium.common.exceptions import NoSuchElementException
import logging
from pyquery import PyQuery
from models import db
from utils import tool
from models import contents_model
from services.searcher import torrent_searcher
from services.rarbg import images


def do_original_source_scrawler(url):
    """ defence broken driver initialization """
    driver = break_defence(url)
    print(driver)
    if driver is False:
        do_original_source_scrawler(url)

    driver.get(url)

    htmls = driver.page_source

    driver.close()

    parse_columns(htmls)


def parse_columns(origin_html_list):
    doc = PyQuery(origin_html_list)

    htmls_list = doc('.lista2').items()

    for html_list in htmls_list:
        column_result_list = parse_column_list(html_list)

        """ defence broken driver initialization """
        driver = break_defence(column_result_list['detail_url'])

        if driver is False:
            parse_columns(origin_html_list)

        driver.get(column_result_list['detail_url'])

        detail_html = driver.page_source

        driver.close()

        column_result_detail = parse_column_detail(detail_html)

        column_result_list['tags'] = column_result_detail['tags']

        torrent_path = torrent_searcher.torrent_download_for_rarbg(column_result_detail['torrent_url'])
        image_path = images.download(column_result_detail['image_url'])

        column_result_list['torrent_url'] = torrent_path
        column_result_list['image_url'] = image_path

        save_data(column_result_list)


def save_data(data):
    db_session = db.init()

    row = db_session.query(contents_model.Contents).filter(contents_model.Contents.unique_id == data['file_hash']).first()

    if row is None:
        new_contents = contents_model.Contents(
            name=data['title'],
            unique_id=data['file_hash'],
            tags=data['tags'],
            type=2,
            thumb_url=data['image_url'],
            torrent_url=data['torrent_url'],
        )

        db_session.add(new_contents)
        db_session.commit()


def parse_column_detail(html):
    tag_list = []

    doc = PyQuery(html)
    torrent_url = doc('table[class="lista"]').find('tr').eq(0).find('td').eq(1).find('a').attr('href')
    image_url = doc('table[class="lista"]').find('tr').eq(3).find('td').eq(1).find('img').attr('src')

    pattern = re.compile('Tags:<\/td>(.*?)<\/tr>')
    tag_result = re.findall(pattern, html)

    if len(tag_result) <= 0:
        tags = ''
    else:
        tag_doc = PyQuery(tag_result[0])
        for tag_a_html in tag_doc('td').find('a').items():
            tag_a_doc = PyQuery(tag_a_html)
            tag_list.append(tag_a_doc('a').text())

        tags = ','.join(tag_list)

    result = {
        'torrent_url': base.SCRAWLER_URL_EURO + torrent_url,
        'image_url': image_url,
        'tags': tags,
    }

    return result


def parse_column_list(html):
    doc = PyQuery(html)

    title = doc('tr').find('td').eq(1).find('a').text()
    detail_url = doc('tr').find('td').eq(1).find('a').attr('href')
    file_hash = tool.hash_with_blake2b(detail_url)

    result = {
        'title': title,
        'detail_url': base.SCRAWLER_URL_EURO + detail_url,
        'file_hash': file_hash[0:10]
    }

    return result


def break_defence(url):
    driver = browser.get_driver()
    driver.get(url)

    time.sleep(6)

    try:
        driver.find_element_by_link_text('Click here').click()

        time.sleep(6)

        driver.save_screenshot('screenshot.png')
        make_screenshot_to_captcha_image()
        captcha_number = solve_captcha_number_from_image('captcha.png')

        driver.find_element_by_id('solve_string').send_keys(captcha_number)

        try:
            time.sleep(2)
            driver.find_element_by_id('button_submit').click()

            logging.info('Break defence step {1} is executing')

            break_success = parse_break_defence_success(driver.page_source)

            if break_success is True:
                return driver
            else:
                driver.close()
                return False
        except NoSuchElementException:
            driver.close()
            return False
    except NoSuchElementException:
        try:
            driver.save_screenshot('screenshot.png')
            make_screenshot_to_captcha_image()
            captcha_number = solve_captcha_number_from_image('captcha.png')

            driver.find_element_by_id("solve_string").send_keys(captcha_number)

            try:
                time.sleep(2)
                driver.find_element_by_id('button_submit').click()

                driver.save_screenshot('screenshot_2.png')

                logging.info('Break defence step {2} is executing')

                break_success = parse_break_defence_success(driver.page_source)

                if break_success is True:
                    return driver
                else:
                    driver.close()
                    return False
            except NoSuchElementException:
                driver.close()
                return False
        except NoSuchElementException:
            logging.info('Break defence step {3} is executing')
            driver.close()
            return False


def break_defence_2(url):
    driver = browser.get_driver()
    driver.get(url)

    time.sleep(6)

    try:
        driver.find_element_by_link_text('Click here').click()

        time.sleep(6)

        driver.save_screenshot('screenshot_torrent_1.png')
        make_screenshot_to_captcha_image()
        captcha_number = solve_captcha_number_from_image('captcha_torrent_1.png')

        driver.find_element_by_id('solve_string').send_keys(captcha_number)

        try:
            time.sleep(2)
            driver.find_element_by_id('button_submit').click()

            logging.info('Break defence step {1} is executing')

            break_success = parse_break_defence_success(driver.page_source)

            if break_success is True:
                return driver
            else:
                driver.close()
                return '11111111'
        except NoSuchElementException:
            driver.close()
            return '22222222222'
    except NoSuchElementException:
        try:
            driver.save_screenshot('screenshot_torrent_2.png')
            make_screenshot_to_captcha_image()
            captcha_number = solve_captcha_number_from_image('captcha_torrent_2.png')

            driver.find_element_by_id("solve_string").send_keys(captcha_number)

            try:
                time.sleep(2)
                driver.find_element_by_id('button_submit').click()

                logging.info('Break defence step {2} is executing')

                break_success = parse_break_defence_success(driver.page_source)

                if break_success is True:
                    return driver
                else:
                    driver.close()
                    return '333333333'
            except NoSuchElementException:
                driver.close()
                return '44444444444'
        except NoSuchElementException:
            logging.info('Break defence step {3} is executing')
            driver.close()
            return '555555555'


def parse_break_defence_success(html):
    pattern = re.compile('mcpslar')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return True
    else:
        return False


def make_screenshot_to_captcha_image():
    im = Image.open('screenshot.png')

    im2 = im.crop((coordinate.X, coordinate.Y, coordinate.X + coordinate.W, coordinate.Y + coordinate.H))
    im2.save('captcha.png')


def form_submit_url_build(last_response):
    captcha_number = solve_captcha_number_from_image()
    captcha_id = parse_captcha_form_ref_captcha_id(last_response.text)
    submitted_bot_captcha = parse_captcha_form_ref_captcha_submitted_bot_captcha(last_response.text)

    form_submit_url = re.sub('r=\w+', 'r=%s', last_response.url)
    form_submit_url = form_submit_url % parse_captcha_form_ref_r(last_response.text)
    form_submit_url = form_submit_url + '&solve_string=' + captcha_number + '&captcha_id=' + captcha_id + '&submitted_bot_captcha=' + submitted_bot_captcha

    return form_submit_url


def parse_captcha_form_defence():
    return '2';


def parse_captcha_form_sk(html):
    pattern = re.compile('name="sk"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_cid(html):
    pattern = re.compile('name="cid"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_i(html):
    pattern = re.compile('name="i"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_ref_cookie(html):
    pattern = re.compile('name="ref_cookie"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_ref_r(html):
    pattern = re.compile('name="r"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_ref_captcha_id(html):
    pattern = re.compile('name="captcha_id"\s+value="(.*?)"')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_captcha_form_ref_captcha_submitted_bot_captcha(html):
    return '1'


def solve_captcha_number_from_image(filename='captcha.png'):
    img = Image.open(filename)
    number = pytesseract.image_to_string(img)

    return number


def parse_js_parameters(html):
    js_sk = parse_js_sk(html)
    js_c = parse_js_c(html)
    js_i = parse_js_i(html)
    js_r = parse_js_r(html)

    result = {
        'js_sk': js_sk,
        'js_c': js_c,
        'js_i': js_i,
        'js_r': js_r
    }

    return result


def parse_js_sk(html):
    pattern = re.compile('var\s+value_sk\s+=\s+\'(.*?)\'')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_js_c(html):
    pattern = re.compile('var\s+value_c\s+=\s+\'(.*?)\'')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_js_i(html):
    pattern = re.compile('var\s+value_i\s+=\s+\'(.*?)\'')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return result[0]
    else:
        return None


def parse_js_r(html):
    pattern = re.compile('r=(.*?)["\']')
    result = re.findall(pattern, html)

    if len(result) > 0:
        res = {
            'r1': result[0],
            'r2': result[1],
            'r3': result[2],
        }

        return res
    else:
        return None


def parse_defence_ajax_url(js_sk=None, js_c=None, js_i=None, js_r=None):
    t = int(round(time.time() * 1000))
    url = base.SCRAWLER_URL_EURO + '/threat_defence_ajax.php?sk=%s&cid=%s&i=%s&r=%s&_=%s' % (js_sk, js_c, js_i, js_r, t)

    return url


def parse_defence_url_2(js_sk=None, js_c=None, js_i=None, js_r=None):
    domain = base.SCRAWLER_URL_EURO.replace('https://', '')
    url = base.SCRAWLER_URL_EURO + '/threat_defence.php?defence=2&sk=%s&cid=%s&i=%s&ref_cookie=%s&r=%s' % (js_sk, js_c, js_i, domain, js_r)

    return url


def parse_captcha_url(html):
    pattern = re.compile('<img\s+src="\/(.*?)"\s+lazyload="off"\s+\/>')
    result = re.findall(pattern, html)

    if len(result) > 0:
        return base.SCRAWLER_URL_EURO + '/' + result[0]
    else:
        return None


def parse_need_one_more_try(html):
    pattern = re.compile('<a\s+href="(.*?)">Click\s+here<\/a>')
    result = re.findall(pattern, html)

    if len(result) > 0:
        res = {
            'need': True,
            'url': base.SCRAWLER_URL_EURO + result[0],
        }
    else:
        res = {
            'need': False,
            'url': '',
        }

    return res