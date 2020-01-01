from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(get_driver_path(), chrome_options=chrome_options)

    return driver


def enable_download_in_headless_chrome(driver, download_dir):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}

    driver.execute("send_command", params)


def get_driver_path():
    path = os.path.abspath(os.curdir) + '/' + 'chromedriver'

    return path