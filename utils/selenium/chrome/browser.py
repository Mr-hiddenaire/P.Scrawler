from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from config import base


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(get_driver_path(), chrome_options=chrome_options)

    return driver


def get_driver_2():
    chrome_options = Options()

    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": base.STATISTICS_PATH + '/torrent/tmp',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(get_driver_path(), chrome_options=chrome_options)

    return driver


def enable_download_in_headless_chrome(driver, download_dir):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}

    driver.execute("send_command", params)


def get_driver_path():
    path = os.path.abspath(os.curdir) + '/' + 'chromedriver'

    return path