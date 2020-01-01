from config import base
import os
from utils import tool
import time
from random import randint
import requests


def download(image_url):
    extension = '.jpg'

    download_images_tmp_path = base.STATISTICS_PATH + '/' + 'images/tmp'
    download_images_path = base.STATISTICS_PATH + '/' + 'images'

    if os.path.exists(download_images_tmp_path) is not True:
        os.makedirs(download_images_tmp_path)

    if os.path.isdir(download_images_tmp_path) is False:
        raise FileNotFoundError('Download images tmp directory does not exists')

    if os.path.isdir(download_images_path) is False:
        raise FileNotFoundError('Download images directory does not exists')

    filename, ext = os.path.splitext(os.path.basename(image_url))

    image_source = requests.get(image_url)

    original_image_filename = download_images_tmp_path + '/' + filename + extension

    with open(original_image_filename, 'wb') as f:
        f.write(image_source.content)

    if os.path.isfile(original_image_filename) is True:
        destination_image_filename = tool.hash_with_blake2b(filename + '_' + str(randint(1, 9999))) + extension
        os.rename(original_image_filename, download_images_path + '/' + destination_image_filename)

        return destination_image_filename