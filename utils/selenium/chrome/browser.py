from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def get_driver():
    chrome_options = Options()

    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(get_driver_path(), chrome_options=chrome_options)

    return driver


def get_driver_path():
    path = os.path.abspath(os.curdir) + '/' + 'chromedriver'

    return path