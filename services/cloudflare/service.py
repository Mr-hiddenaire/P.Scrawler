import cfscrape


def get_data(url):
    scraper = cfscrape.create_scraper()

    content = scraper.get(url).content.decode("utf-8")

    return content
