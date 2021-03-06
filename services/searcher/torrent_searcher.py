import requests
from config import searcher
from pyquery import PyQuery
import json
from selenium.common.exceptions import NoSuchElementException
from config import base
from utils.selenium.chrome import browser
import os
from utils import tool
import time
from random import randint
from services.rarbg import service as rarbg_service
import logging
from urllib.parse import urlparse
import re


def find_torrent(unique_id):
    g_cse_api = searcher.GOOGLE_API_URL % (unique_id, searcher.GOOGLE_CSE_CX, searcher.GOOGLE_CSE_API_KEY)

    response = requests.get(g_cse_api, headers={'User-Agent': base.USER_AGENT})

    logging.info('G-CES.result: ' + response.text)

    json_result = json.loads(response.text)

    """ G CSE retrieve fail """
    if 'items' not in json_result:
        return None

    g_cse_items = json_result['items']

    for g_cse_item in g_cse_items:
        if g_cse_item['displayLink'] in searcher.SEARCH_TARGET_DOMAINS:

            func_name = searcher.SEARCH_TARGET_DOMAINS[g_cse_item['displayLink']]

            func_name = 'parse_' + func_name

            torrent_url = eval(func_name)(g_cse_item['link'], unique_id)

            if torrent_url is not None:
                torrent_path = torrent_download_for_library(torrent_url)
                return torrent_path
            else:
                continue

    return None


def torrent_download_for_library(torrent_url):
    extension_list = ['.torrent']
    counter = 1

    download_torrent_tmp_path = base.STATISTICS_PATH + '/' + 'torrent/tmp'
    download_torrent_path = base.STATISTICS_PATH + '/' + 'torrent'

    if os.path.exists(download_torrent_tmp_path) is not True:
        os.makedirs(download_torrent_tmp_path)

    if os.path.isdir(download_torrent_tmp_path) is False:
        raise FileNotFoundError('Download torrent tmp directory does not exists')

    if os.path.isdir(download_torrent_path) is False:
        raise FileNotFoundError('Download torrent directory does not exists')

    """ driver initialization """
    driver = browser.get_driver()

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_torrent_tmp_path}}

    driver.execute("send_command", params)

    driver.get(torrent_url)

    """ wait to download finished """
    time.sleep(5)

    while True:
        time.sleep(1)

        if counter > 5:
            driver.close()
            return None

        counter = counter + 1

        torrent_filename_list = os.listdir(download_torrent_tmp_path)

        if len(torrent_filename_list) <= 0:
            continue
        else:
            original_torrent_filename = torrent_filename_list[0]
            filename, extension = os.path.splitext(original_torrent_filename)

            if extension in extension_list:
                destination_torrent_filename = tool.hash_with_blake2b(filename + '_' + str(randint(1, 9999)))  + extension

                os.rename(download_torrent_tmp_path + '/' + original_torrent_filename, download_torrent_path + '/' + destination_torrent_filename)

                driver.close()
                return destination_torrent_filename
            else:
                driver.close()
                return None


def torrent_download_for_rarbg(torrent_url, driver):
    extension_list = ['.torrent']
    counter = 1

    screenshot_filename = 'screenshot.png'
    captcha_filename = 'captcha.png'

    download_torrent_tmp_path = base.STATISTICS_PATH + '/' + 'torrent/tmp'
    download_torrent_path = base.STATISTICS_PATH + '/' + 'torrent'

    if os.path.exists(download_torrent_tmp_path) is not True:
        os.makedirs(download_torrent_tmp_path)

    if os.path.isdir(download_torrent_tmp_path) is False:
        raise FileNotFoundError('Download torrent tmp directory does not exists')

    if os.path.isdir(download_torrent_path) is False:
        raise FileNotFoundError('Download torrent directory does not exists')

    try:
        driver.get(torrent_url)
        time.sleep(6)

        driver.find_element_by_link_text('Click here').click()
        driver.save_screenshot(screenshot_filename)
        rarbg_service.make_screenshot_to_captcha_image(screenshot_filename, captcha_filename)
        captcha_number = rarbg_service.solve_captcha_number_from_image(captcha_filename)

        driver.find_element_by_id('solve_string').send_keys(captcha_number)
        driver.find_element_by_id('button_submit').click()

        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_torrent_tmp_path}}
        driver.execute("send_command", params)
        driver.get(torrent_url)
    except NoSuchElementException:
        try:
            driver.get(torrent_url)
            time.sleep(6)

            driver.save_screenshot(screenshot_filename)
            rarbg_service.make_screenshot_to_captcha_image(screenshot_filename, captcha_filename)
            captcha_number = rarbg_service.solve_captcha_number_from_image(captcha_filename)

            driver.find_element_by_id('solve_string').send_keys(captcha_number)

            driver.find_element_by_id('button_submit').click()

            driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_torrent_tmp_path}}
            driver.execute("send_command", params)
            driver.get(torrent_url)
        except NoSuchElementException:
            driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_torrent_tmp_path}}
            driver.execute("send_command", params)
            driver.get(torrent_url)

    """ wait to download finished """
    time.sleep(5)

    while True:
        time.sleep(1)

        if counter > 5:
            return None

        counter = counter + 1

        torrent_filename_list = os.listdir(download_torrent_tmp_path)

        if len(torrent_filename_list) <= 0:
            continue
        else:
            original_torrent_filename = torrent_filename_list[0]
            filename, extension = os.path.splitext(original_torrent_filename)

            if extension in extension_list:
                destination_torrent_filename = tool.hash_with_blake2b(
                    filename + '_' + str(randint(1, 9999))) + extension

                os.rename(download_torrent_tmp_path + '/' + original_torrent_filename, download_torrent_path + '/' + destination_torrent_filename)
                return destination_torrent_filename
            else:
                return None


def parse_1337x(url, unique_id):
    """
    response = requests.get(url, headers={'User-Agent': base.USER_AGENT})
    doc = PyQuery(response.text)

    """

    """ driver initialization """
    driver = browser.get_driver()

    driver.get(url)

    doc = PyQuery(driver.page_source)

    download_url_html = doc('.dropdown-menu li').eq(0)

    download_url_doc = doc(download_url_html)

    torrent_url = download_url_doc('a').attr('href')

    if torrent_url is not None:

        torrent_url = torrent_url.replace('http', 'https')

        torrent_is_valid = is_valid_torrent_judged_via_http_status(torrent_url)

        if torrent_is_valid is True:
            driver.close()
            return torrent_url
        else:
            """ Parse out the torrent, but it maybe invalid """
            driver.close()
            return None
    else:
        driver.close()
        torrent_url = parse_1337x_extra(url, unique_id)
        return torrent_url


def parse_1337x_extra(url, unique_id):

    """ driver initialization """
    driver = browser.get_driver()

    driver.get(url)
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

    new_url = domain + '/search/' + unique_id + '/1/'

    driver.get(new_url)

    doc = PyQuery(driver.page_source)

    for html in doc('tbody tr').items():
        doc = PyQuery(html)
        page_url = doc('td a').eq(1).attr('href')
        title = doc('td a').eq(1).text()

        pattern = re.compile(unique_id)
        result = re.findall(pattern, title)

        if len(result) > 0:
            driver.get(domain + page_url)

            doc = PyQuery(driver.page_source)

            download_url_html = doc('.dropdown-menu li').eq(0)

            download_url_doc = doc(download_url_html)

            torrent_url = download_url_doc('a').attr('href')

            torrent_url = torrent_url.replace('http', 'https')

            driver.close()
            return torrent_url
        else:
            continue

    return None


def parse_limetorrents(url, unique_id):
    """
    response = requests.get(url, headers={'User-Agent': base.USER_AGENT})

    doc = PyQuery(response.text)

    """

    """ driver initialization """
    driver = browser.get_driver()

    driver.get(url)

    doc = PyQuery(driver.page_source)

    torrent_url = doc('.downloadarea').eq(0).find('a').attr('href')

    if torrent_url is not None:
        torrent_url = torrent_url.replace('http', 'https')

        torrent_is_valid = is_valid_torrent_judged_via_http_status(torrent_url)

        if torrent_is_valid is True:
            driver.close()
            return torrent_url
        else:
            """ Parse out the torrent, but it maybe invalid """
            driver.close()
            return None
    else:
        driver.close()
        return None


""" To judge whether torrent is valid or not via response history """
def is_valid_torrent_judged_via_http_status(torrent_url):
    response = requests.get(torrent_url, headers={'User-Agent': base.USER_AGENT})

    """ There is history,it indicates invalid """
    if len(response.history) <= 0:
        return True
    else:
        return False
