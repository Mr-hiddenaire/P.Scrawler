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

            torrent_url = eval(func_name)(g_cse_item['link'])

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

    download_torrent_tmp_path = base.STATISTICS_PATH + '/' + 'torrent/tmp'
    download_torrent_path = base.STATISTICS_PATH + '/' + 'torrent'

    if os.path.exists(download_torrent_tmp_path) is not True:
        os.makedirs(download_torrent_tmp_path)

    if os.path.isdir(download_torrent_tmp_path) is False:
        raise FileNotFoundError('Download torrent tmp directory does not exists')

    if os.path.isdir(download_torrent_path) is False:
        raise FileNotFoundError('Download torrent directory does not exists')

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_torrent_tmp_path}}

    driver.execute("send_command", params)

    driver.get(torrent_url)

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
                destination_torrent_filename = tool.hash_with_blake2b(
                    filename + '_' + str(randint(1, 9999))) + extension

                os.rename(download_torrent_tmp_path + '/' + original_torrent_filename,
                          download_torrent_path + '/' + destination_torrent_filename)
                driver.close()
                return destination_torrent_filename
            else:
                driver.close()
                return None


def parse_1337x(url):
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
        return None


def parse_limetorrents(url):
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
