from bs4 import BeautifulSoup
import dateutil
import pandas as pd

def parse_telegram_html(data):
    data_list = []
    soup = BeautifulSoup(data, 'html.parser')
    tz = None
    for div in soup.select("div.message.default"):
        body = div.find('div', class_='body')
        from_name_ = body.find('div', class_='from_name')
        if from_name_ is not None and from_name_.find('span') is None:
            username = from_name_.string.strip()
            raw_date = body.find('div', class_='date')['title']
            naiv_timestamp = dateutil.parser.parse(raw_date)
            timestamp = naiv_timestamp.astimezone(tz) if tz else naiv_timestamp
            links = [l.get('href') for l in body.find_all('a')]

        if body.find('div', class_='media_wrap clearfix') is None:
            text = body.find('div', class_='text').get_text().strip()
        else:
            text = 'media-ommited'

        data_list.append({"username": username,
                          "date": timestamp,
                          "message": text,
                          "links": links})

    return pd.DataFrame(data_list)
