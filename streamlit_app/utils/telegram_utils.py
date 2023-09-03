from bs4 import BeautifulSoup
import dateutil
import pandas as pd

def parse_telegram_html(data):
    data_list = []
    soup = BeautifulSoup(data, 'html.parser')
    for div in soup.select("div.message.default"):
        body = div.find('div', class_='body')
        from_name_ = body.find('div', class_='from_name')
        if from_name_ is not None and from_name_.find('span') is None:
            username = from_name_.string.strip()
            raw_date = body.find('div', class_='date')['title']
            timestamp = dateutil.parser.parse(raw_date)
            links = [l.get('href') for l in body.find_all('a')]

        if body.find('div', class_='media_wrap clearfix') is None:
            text = body.find('div', class_='text').get_text().strip()
        else:
            text = '<Media omitted>'

        data_list.append({"username": username, "date": timestamp, "message": text, "links": links})

    return pd.DataFrame(data_list)

#
#
# from transformers import pipeline
#
# def try_huf():
#     summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")
#
#     conversation = '''Jeff: Can I train a 🤗 Transformers model on Amazon SageMaker?
#     Philipp: Sure you can use the new Hugging Face Deep Learning Container.
#     Jeff: ok.
#     Jeff: and how can I get started?
#     Jeff: where can I find documentation?
#     Philipp: ok, ok you can find everything here. https://huggingface.co/blog/the-partnership-amazon-sagemaker-and-hugging-face
#     '''
#
#     return summarizer(conversation)
#
# print(try_huf())

# import torch
# import torchvision
# import torchaudio
