from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
import csv
import os

duplicate_link = set()
file = "./result/test.csv"
has_previous_file = False


def get_new_detail(link):
    result = {}
    url = requests.get(link)
    soup = BeautifulSoup(url.content, "html.parser")
    head_data = soup.find("h1")
    result['head'] = head_data.text
    # data = soup.find("h2",{"class":"display-post-title"})
    content_data = soup.select('div[class*="-RichTextContainer"]')
    content_string = ''.join(map(str, map(lambda x: x.text, content_data)))
    result['content'] = content_string
    writer_data = soup.select('div[class*="-TextContributorName "]').pop().text if soup.select(
        'div[class*="-TextContributorName "]') else "no writer"
    result["writer"] = writer_data
    if soup.select_one('div[data-component="image-block"]'):
        img_link = soup.select_one('div[data-component="image-block"]')
        img_link = img_link.select_one('img')
        result["img_link"] = img_link.attrs['src']
    else:
        result["img_link"] = "no image"

    date = re.search('datePublished":"(.*?)T', str(url.content))
    if date:
        date_data = datetime.strptime(date.group(1), '%Y-%m-%d')
    else:
        date = soup.select_one('div[class*="FooterContainer"]')
        date = date.select_one('time[data-testid="timestamp"]')
        date_data = datetime.strptime(date.attrs["datetime"], '%Y-%m-%dT%H:%M:%S.000Z')

    result["date"] = date_data
    return result


# Check and Read previous csv and collet duplicate url
if os.path.isfile(file):
    has_previous_file = True
    with open(file) as fp:
        reader = csv.DictReader(fp, delimiter="|")
        data_read = [row for row in reader]
        duplicate_link = set(map(lambda x: x['link'], data_read))

# Get RSS FEED
url = requests.get("https://feeds.bbci.co.uk/news/world/rss.xml")
soup = BeautifulSoup(url.content, features='xml')
data = soup.find_all("item")

# Write File
with open(file, "a+", newline="") as fp:
    writer = csv.writer(fp, delimiter="|")
    if not has_previous_file:
        writer.writerow(["head", "content", "img", "date", "writer", "link"])
    for i in data:
        try:
            link = i.find("link")
            print('Crawling → ' + link.text)
            if link.text in duplicate_link:
                continue
            duplicate_link.add(link.text)
            result = get_new_detail(link.text)
            result['link'] = link.text
            writer.writerow([result['head'], result['content'], result['img_link'], result['date'], result['writer'],result['link']])
        except:
            continue
